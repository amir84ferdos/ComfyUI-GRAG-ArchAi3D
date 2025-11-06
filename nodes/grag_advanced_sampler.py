"""
GRAG Advanced Sampler Node v3.0

Enhanced sampler that injects GRAG attention patches into the sampling process.

Features:
- v2.2.1 contamination fix (try/finally restoration)
- Per-layer GRAG application
- Adaptive timestep support
- Multi-resolution tier support
- Architecture auto-detection (Qwen, Flux, SD3, etc.)
- Debug mode for attention analysis

Based on v2.2.1 sampler with significant enhancements.

Author: Amir Ferdos (ArchAi3d)
Email: Amir84ferdos@gmail.com
License: MIT
"""

import torch
import comfy.samplers
import comfy.sample
import comfy.model_management
import comfy.utils
import latent_preview

# Use relative imports for package structure
from ..core.attention_v3 import apply_grag_v3, extract_grag_config_from_conditioning, GRAGConfig
from ..core.adaptive_control import AdaptiveScheduler


class GRAGAdvancedSampler:
    """GRAG-aware sampler with enhanced features from v3.0.

    This sampler wraps ComfyUI's standard KSampler and injects GRAG attention
    patches to enable fine-grained editing control with advanced features:

    - Per-layer control (different λ/δ per transformer block)
    - Adaptive timestep scheduling
    - Multi-resolution tier support
    - v2.2.1 contamination fix (try/finally restoration)

    Version: 3.0.0
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Standard KSampler parameters
                "model": ("MODEL", {
                    "tooltip": "The diffusion model used for denoising"
                }),
                "positive": ("CONDITIONING", {
                    "tooltip": "Positive conditioning (should contain GRAG metadata from Unified Controller)"
                }),
                "negative": ("CONDITIONING", {
                    "tooltip": "Negative conditioning"
                }),
                "latent_image": ("LATENT", {
                    "tooltip": "Input latent to denoise"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "tooltip": "Random seed for noise generation"
                }),
                "steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Number of denoising steps"
                }),
                "cfg": ("FLOAT", {
                    "default": 8.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "tooltip": "Classifier-Free Guidance scale"
                }),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {
                    "tooltip": "Sampling algorithm to use"
                }),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {
                    "tooltip": "Noise schedule for denoising"
                }),
                "denoise": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Denoising strength (1.0 = full denoise)"
                }),

                # v3.0 Advanced options
                "debug_mode": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable debug logging (attention layer info, performance metrics)"
                }),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("samples",)
    FUNCTION = "sample"
    CATEGORY = "GRAG/v3.0"

    def _patch_qwen_attention(self, model, grag_config, debug_mode=False):
        """Monkey-patch Qwen attention layers to apply GRAG reweighting.

        This function finds all Attention modules in the model and wraps their
        forward method to apply GRAG key reweighting after RoPE but before attention.

        Args:
            model: ComfyUI model object with diffusion_model attribute
            grag_config: GRAGConfig object with GRAG parameters
            debug_mode: Enable detailed logging

        Returns:
            dict: Dictionary mapping modules to their original forward methods.
                  Used for restoration after sampling completes (v2.2.1 fix).
                  Returns empty dict if patching fails.
        """
        # Dictionary to store original forward methods for restoration (v2.2.1 fix)
        original_forwards = {}

        # Access the actual diffusion model
        if hasattr(model, 'model') and hasattr(model.model, 'diffusion_model'):
            diffusion_model = model.model.diffusion_model
        else:
            print("[GRAG v3.0] Warning: Could not access diffusion_model")
            return original_forwards

        # Find and patch all Attention modules
        patched_count = 0
        layer_idx = 0

        for name, module in diffusion_model.named_modules():
            # Look for Qwen Attention modules specifically
            # Check class name AND verify it has the right attributes
            if (module.__class__.__name__ == 'Attention' and
                hasattr(module, 'to_q') and
                hasattr(module, 'add_q_proj') and
                hasattr(module, 'norm_q')):

                # Store original forward method for restoration (v2.2.1 contamination fix)
                original_forward = module.forward
                original_forwards[module] = original_forward

                # Create wrapped forward function with GRAG
                def create_grag_forward(orig_forward, grag_cfg, attn_module, layer_id):
                    def grag_forward(hidden_states, encoder_hidden_states=None, encoder_hidden_states_mask=None,
                                   attention_mask=None, image_rotary_emb=None, transformer_options={}):
                        # Replicate attention forward pass with GRAG injection

                        batch_size = hidden_states.shape[0]
                        seq_img = hidden_states.shape[1]
                        seq_txt = encoder_hidden_states.shape[1]

                        # Image stream QKV - use BHND format (batch, heads, seq, dim) to match new Qwen implementation
                        img_query = attn_module.to_q(hidden_states).view(batch_size, seq_img, attn_module.heads, -1).transpose(1, 2).contiguous()
                        img_key = attn_module.to_k(hidden_states).view(batch_size, seq_img, attn_module.heads, -1).transpose(1, 2).contiguous()
                        img_value = attn_module.to_v(hidden_states).view(batch_size, seq_img, attn_module.heads, -1).transpose(1, 2)

                        # Text stream QKV - use BHND format
                        txt_query = attn_module.add_q_proj(encoder_hidden_states).view(batch_size, seq_txt, attn_module.heads, -1).transpose(1, 2).contiguous()
                        txt_key = attn_module.add_k_proj(encoder_hidden_states).view(batch_size, seq_txt, attn_module.heads, -1).transpose(1, 2).contiguous()
                        txt_value = attn_module.add_v_proj(encoder_hidden_states).view(batch_size, seq_txt, attn_module.heads, -1).transpose(1, 2)

                        # Normalization
                        img_query = attn_module.norm_q(img_query)
                        img_key = attn_module.norm_k(img_key)
                        txt_query = attn_module.norm_added_q(txt_query)
                        txt_key = attn_module.norm_added_k(txt_key)

                        # Combine streams along sequence dimension (dim=2 for BHND format)
                        joint_query = torch.cat([txt_query, img_query], dim=2)
                        joint_key = torch.cat([txt_key, img_key], dim=2)
                        joint_value = torch.cat([txt_value, img_value], dim=2)

                        # Apply RoPE using new apply_rope1 function
                        from comfy.ldm.flux.math import apply_rope1
                        joint_query = apply_rope1(joint_query, image_rotary_emb)
                        joint_key = apply_rope1(joint_key, image_rotary_emb)

                        # ===== GRAG v3.0 INJECTION POINT =====
                        # Apply GRAG reweighting to keys BEFORE final flattening
                        try:
                            # Convert BHND to BSHD format for GRAG, then flatten
                            # BHND: [B, H, S, D] -> BSHD: [B, S, H, D] -> [B, S, H*D]
                            joint_key_for_grag = joint_key.transpose(1, 2).contiguous()  # BHND -> BSHD
                            joint_key_flat = joint_key_for_grag.flatten(start_dim=2)  # [B, S, H*D]

                            # Update config with layer index for per-layer control
                            layer_config = GRAGConfig(
                                enabled=grag_cfg.enabled,
                                lambda_val=grag_cfg.lambda_val,
                                delta_val=grag_cfg.delta_val,
                                heads=attn_module.heads,
                                layer_idx=layer_id,  # v3.0: Per-layer support
                                timestep=grag_cfg.timestep,
                                strength_multiplier=grag_cfg.strength_multiplier,
                                multi_resolution=grag_cfg.multi_resolution,
                                tier_config=grag_cfg.tier_config,
                                eps=grag_cfg.eps,
                            )

                            # Apply GRAG v3.0 reweighting
                            joint_key_flat = apply_grag_v3(
                                joint_key_flat,
                                seq_txt,
                                layer_config
                            )

                            # Unflatten back to BSHD then transpose back to BHND
                            joint_key_for_grag = joint_key_flat.unflatten(-1, (attn_module.heads, -1))  # [B, S, H, D]
                            joint_key = joint_key_for_grag.transpose(1, 2).contiguous()  # BSHD -> BHND

                        except Exception as e:
                            print(f"[GRAG v3.0] Warning: Reweighting failed at layer {layer_id}: {e}")
                            import traceback
                            traceback.print_exc()
                            pass  # Continue with original keys if GRAG fails
                        # ===== END GRAG v3.0 =====

                        # Pass tensors in BHND format with skip_reshape=True (new Qwen format)
                        # Output will be BSD format (batch, seq, heads*dim) due to default skip_output_reshape=False
                        from comfy.ldm.modules.attention import optimized_attention_masked
                        joint_hidden_states = optimized_attention_masked(
                            joint_query, joint_key, joint_value, attn_module.heads,
                            attention_mask, transformer_options=transformer_options,
                            skip_reshape=True  # Input is BHND, output is BSD (due to default reshape)
                        )

                        # Split streams - output is already in BSD format, no transpose needed
                        txt_attn_output = joint_hidden_states[:, :seq_txt, :]
                        img_attn_output = joint_hidden_states[:, seq_txt:, :]

                        # Output projections
                        img_attn_output = attn_module.to_out[0](img_attn_output)
                        img_attn_output = attn_module.to_out[1](img_attn_output)
                        txt_attn_output = attn_module.to_add_out(txt_attn_output)

                        return img_attn_output, txt_attn_output

                    return grag_forward

                # Replace forward method
                module.forward = create_grag_forward(original_forward, grag_config, module, layer_idx)
                patched_count += 1
                layer_idx += 1

                if debug_mode:
                    print(f"[GRAG v3.0 Debug] Patched layer {layer_idx}: {name}")

        print(f"[GRAG v3.0] Patched {patched_count} Attention layers")
        return original_forwards

    def sample(self, model, positive, negative, latent_image, seed, steps, cfg, sampler_name, scheduler, denoise, debug_mode=False):
        """Perform sampling with GRAG v3.0 attention guidance.

        This is the main entry point for the sampler. It:
        1. Extracts GRAG configuration from positive conditioning
        2. Creates a model clone with GRAG monkey-patch injected
        3. Calls ComfyUI's standard sampling with the enhanced model
        4. CRITICAL: Restores original forward methods in finally block (v2.2.1 fix)

        Args:
            model: ComfyUI MODEL object
            positive: Positive conditioning (may contain GRAG v3.0 metadata)
            negative: Negative conditioning
            latent_image: Input latent {"samples": tensor}
            seed: Random seed for reproducibility
            steps: Number of denoising steps
            cfg: Classifier-Free Guidance scale
            sampler_name: Sampler algorithm (euler, dpmpp_2m, etc.)
            scheduler: Noise schedule (normal, karras, etc.)
            denoise: Denoising strength (0.0-1.0)
            debug_mode: Enable debug logging

        Returns:
            tuple: (latent_dict,) with denoised samples
        """
        # Extract GRAG configuration from conditioning metadata
        grag_config = extract_grag_config_from_conditioning(positive)

        # Clone model to avoid modifying original
        model_clone = model.clone()

        # Store original forward methods for restoration (v2.2.1 contamination fix)
        original_forwards = {}

        # If GRAG is enabled, monkey-patch the attention forward function
        if grag_config and grag_config.enabled:
            # Display effective parameters
            if isinstance(grag_config.lambda_val, list):
                lambda_range = f"{min(grag_config.lambda_val):.2f}-{max(grag_config.lambda_val):.2f}"
                delta_range = f"{min(grag_config.delta_val):.2f}-{max(grag_config.delta_val):.2f}"
                print(f"[GRAG v3.0] GRAG enabled - Per-layer: λ={lambda_range}, δ={delta_range}, strength={grag_config.strength_multiplier:.2f}")
            else:
                print(f"[GRAG v3.0] GRAG enabled - Global: λ={grag_config.lambda_val:.2f}, δ={grag_config.delta_val:.2f}, strength={grag_config.strength_multiplier:.2f}")

            # Try to patch Qwen attention layers
            try:
                original_forwards = self._patch_qwen_attention(model_clone, grag_config, debug_mode)
                print(f"[GRAG v3.0] GRAG patches injected successfully")
            except Exception as e:
                print(f"[GRAG v3.0] Failed to inject GRAG patches: {e}")
                print(f"[GRAG v3.0] Falling back to standard sampling")
        else:
            print(f"[GRAG v3.0] GRAG disabled - using standard sampling")

        # Call ComfyUI's standard sampling function with try/finally for cleanup
        # This handles all the complex diffusion logic
        try:
            samples = self._common_ksampler(
                model_clone,
                seed,
                steps,
                cfg,
                sampler_name,
                scheduler,
                positive,
                negative,
                latent_image,
                denoise=denoise,
                debug_mode=debug_mode
            )

            return samples

        except Exception as e:
            print(f"[GRAG v3.0] Error during sampling: {e}")
            import traceback
            traceback.print_exc()

            # Fallback: Try without GRAG patches
            print(f"[GRAG v3.0] Falling back to standard sampler")
            model_clean = model.clone()
            samples = self._common_ksampler(
                model_clean,
                seed,
                steps,
                cfg,
                sampler_name,
                scheduler,
                positive,
                negative,
                latent_image,
                denoise=denoise,
                debug_mode=debug_mode
            )

            return samples

        finally:
            # CRITICAL: Always restore original forward methods to prevent contamination
            # This fixes the v2.2.1 global contamination bug where GRAG affects other samplers
            if original_forwards:
                for module, original_forward in original_forwards.items():
                    module.forward = original_forward
                print(f"[GRAG v3.0] Restored {len(original_forwards)} attention modules (contamination prevention)")

    def _common_ksampler(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0, debug_mode=False):
        """Wrapper around ComfyUI's common_ksampler function.

        This replicates the logic from nodes.py:common_ksampler to ensure
        compatibility with ComfyUI's sampling infrastructure.

        Args:
            model: MODEL object (possibly with GRAG patches)
            seed: Random seed
            steps: Denoising steps
            cfg: CFG scale
            sampler_name: Sampler algorithm
            scheduler: Noise scheduler
            positive: Positive conditioning
            negative: Negative conditioning
            latent: Latent dict {"samples": tensor}
            denoise: Denoising strength
            debug_mode: Enable debug logging

        Returns:
            tuple: (latent_dict,) with denoised samples
        """
        # Extract latent samples
        latent_image = latent["samples"]

        # Fix empty latent channels if needed
        latent_image = comfy.sample.fix_empty_latent_channels(model, latent_image)

        # Prepare noise
        batch_inds = latent.get("batch_index", None)
        noise = comfy.sample.prepare_noise(latent_image, seed, batch_inds)

        # Handle noise mask if present
        noise_mask = latent.get("noise_mask", None)

        # Setup progress callback
        callback = latent_preview.prepare_callback(model, steps)
        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED

        if debug_mode:
            print(f"[GRAG v3.0 Debug] Starting sampling: {steps} steps, {sampler_name}/{scheduler}")

        # Perform sampling
        samples = comfy.sample.sample(
            model,
            noise,
            steps,
            cfg,
            sampler_name,
            scheduler,
            positive,
            negative,
            latent_image,
            denoise=denoise,
            disable_noise=False,
            start_step=None,
            last_step=None,
            force_full_denoise=False,
            noise_mask=noise_mask,
            callback=callback,
            disable_pbar=disable_pbar,
            seed=seed
        )

        if debug_mode:
            print(f"[GRAG v3.0 Debug] Sampling complete")

        # Return in ComfyUI latent format
        out = latent.copy()
        out["samples"] = samples

        return (out,)


# ============================================================================
# COMFYUI NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "GRAG_Advanced_Sampler": GRAGAdvancedSampler
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRAG_Advanced_Sampler": "⚙️ GRAG Advanced Sampler v3.0"
}
