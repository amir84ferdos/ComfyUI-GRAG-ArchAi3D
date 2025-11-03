"""
GRAG Simple Controller Node v3.0

Simplified interface for GRAG attention control - beginner-friendly!

Features:
- Preset-based control (no manual parameters needed)
- Enable/disable toggle
- Strength slider for easy intensity adjustment
- Clean, minimal UI

Perfect for users who want GRAG effects without complexity.

Author: Amir Ferdos (ArchAi3d)
Email: Amir84ferdos@gmail.com
License: MIT
"""

import copy

# Use relative imports for package structure
from ..core.preset_loader import get_preset_loader


class GRAGSimpleController:
    """GRAG Simple Controller - Beginner-friendly preset-based control.

    This simplified controller provides easy access to GRAG effects through
    presets only, without exposing advanced parameters. Perfect for users
    who want results without technical complexity.

    Version: 3.0.0
    """

    def __init__(self):
        self.preset_loader = get_preset_loader()

    @classmethod
    def INPUT_TYPES(cls):
        # Load preset names dynamically
        preset_loader = get_preset_loader()
        preset_names = preset_loader.get_all_preset_names()

        # Filter to show only recommended presets for beginners
        # Keep "Custom" + paper presets + v2.2.1 presets + Clean Room presets
        recommended_presets = []
        for name in preset_names:
            name_lower = name.lower()
            # Include: Custom, Paper presets, v2.2.1 Balanced, Clean Room presets
            if (name == "Custom" or
                "paper:" in name_lower or
                name == "v2.2.1: Balanced" or
                "clean room:" in name_lower):
                recommended_presets.append(name)

        # If filtering resulted in empty list, use all presets
        if not recommended_presets:
            recommended_presets = preset_names

        return {
            "required": {
                # Input conditioning from any encoder
                "conditioning": ("CONDITIONING", {
                    "tooltip": "Conditioning from any encoder (Qwen, Flux, SD3, etc.)"
                }),

                # Main enable/disable toggle
                "enable_grag": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable GRAG attention guidance (turns effect on/off)"
                }),

                # Preset selector (filtered to recommended presets)
                "preset": (recommended_presets, {
                    "default": "Paper: Balanced" if "Paper: Balanced" in recommended_presets else recommended_presets[0],
                    "tooltip": "Choose a preset effect - 'Paper: Balanced' is recommended for beginners"
                }),

                # Simple strength slider (scales effect from neutral)
                "strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "Effect intensity: 0.0=no change, 0.1=minimal, 1.0=preset's intended effect, 2.0=very strong"
                }),
            },
            "optional": {
                # Manual λ/δ override (for advanced control)
                "lambda_override": ("FLOAT", {
                    "default": -1.0,
                    "min": -1.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Manual λ (lambda) override. -1.0=use preset+strength, 0.1-2.0=custom value (1.0=neutral)"
                }),
                "delta_override": ("FLOAT", {
                    "default": -1.0,
                    "min": -1.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Manual δ (delta) override. -1.0=use preset+strength, 0.1-2.0=custom value (1.0=neutral)"
                }),
            }
        }

    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    FUNCTION = "apply_grag_simple"
    CATEGORY = "GRAG/v3.0"

    def apply_grag_simple(
        self,
        conditioning,
        enable_grag,
        preset,
        strength,
        lambda_override=-1.0,
        delta_override=-1.0,
    ):
        """Apply GRAG configuration to conditioning (simplified version).

        This simplified version only uses presets and a strength multiplier,
        making it easy for beginners to get started with GRAG.

        Args:
            conditioning: Input conditioning from encoder
            enable_grag: Enable/disable GRAG effects
            preset: Preset name to use
            strength: Overall strength multiplier (0.0-2.0)
            lambda_override: Optional manual λ override (-1.0=use preset, 0.1-2.0=custom)
            delta_override: Optional manual δ override (-1.0=use preset, 0.1-2.0=custom)

        Returns:
            tuple: (modified_conditioning,)
        """
        # Passthrough mode: GRAG disabled
        if not enable_grag:
            print("[GRAG Simple] GRAG disabled - passthrough mode")
            return (conditioning,)

        # Load preset configuration
        if preset != "Custom":
            preset_config = self.preset_loader.get_preset_by_name(preset)
            lambda_base = preset_config.get("lambda", 1.0)
            delta_base = preset_config.get("delta", 1.05)
            preset_strength = preset_config.get("strength", 1.0)

            print(f"[GRAG Simple] Preset: {preset}")
            print(f"[GRAG Simple] Base parameters: λ={lambda_base:.2f}, δ={delta_base:.2f}")
            print(f"[GRAG Simple] Strength slider: {strength:.2f}")

            # Scale λ and δ towards/away from neutral (1.0) based on strength
            # strength=0.0 → λ=1.0, δ=1.0 (no effect)
            # strength=1.0 → λ=preset, δ=preset (original preset)
            # strength=2.0 → λ and δ deviate even more from 1.0

            # Calculate deviation from neutral
            lambda_deviation = lambda_base - 1.0  # How far λ is from neutral
            delta_deviation = delta_base - 1.0    # How far δ is from neutral

            # Scale deviations by strength
            lambda_val = 1.0 + (lambda_deviation * strength)
            delta_val = 1.0 + (delta_deviation * strength)

            print(f"[GRAG Simple] Scaled parameters: λ={lambda_val:.3f}, δ={delta_val:.3f}")
        else:
            # Custom mode: scale from neutral based on strength
            # At strength=1.0, use reasonable visible values
            lambda_val = 1.0 + (0.2 * strength)   # strength=1.0 → λ=1.2
            delta_val = 1.0 + (0.3 * strength)    # strength=1.0 → δ=1.3
            preset_strength = 1.0

            print(f"[GRAG Simple] Custom mode")
            print(f"[GRAG Simple] Strength: {strength:.2f}")
            print(f"[GRAG Simple] Auto-calculated: λ={lambda_val:.3f}, δ={delta_val:.3f}")

        # Apply manual overrides if provided (ignores preset and strength)
        if lambda_override >= 0.0:
            # Clamp to valid range
            lambda_val = max(0.1, min(2.0, lambda_override))
            print(f"[GRAG Simple] λ override: {lambda_val:.3f} (manual)")

        if delta_override >= 0.0:
            # Clamp to valid range
            delta_val = max(0.1, min(2.0, delta_override))
            print(f"[GRAG Simple] δ override: {delta_val:.3f} (manual)")

        # Store strength for metadata
        final_strength = strength

        # Build GRAG metadata (compatible with v3.0 Advanced Sampler)
        grag_cond = copy.deepcopy(conditioning)

        # Add GRAG configuration to conditioning metadata
        for i in range(len(grag_cond)):
            if len(grag_cond[i]) >= 2:
                # Get or create metadata dict
                metadata = grag_cond[i][1].copy() if isinstance(grag_cond[i][1], dict) else {}

                # v3.0 format (primary)
                metadata['grag_enabled'] = True
                metadata['grag_lambda'] = lambda_val
                metadata['grag_delta'] = delta_val
                metadata['grag_strength_multiplier'] = final_strength

                # v2.2.1 backward compatibility
                metadata['grag_cond_b'] = lambda_val
                metadata['grag_cond_delta'] = delta_val
                metadata['grag_strength'] = final_strength

                # Mark as simple mode
                metadata['grag_control_mode'] = 'simple'

                # Update conditioning
                grag_cond[i] = (grag_cond[i][0], metadata)

        print(f"[GRAG Simple] Configuration embedded in conditioning")
        print(f"[GRAG Simple] Final strength: {final_strength:.2f}")
        print(f"[GRAG Simple] Use 'GRAG Advanced Sampler' to apply effects")

        return (grag_cond,)


# ============================================================================
# COMFYUI NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "GRAG_Simple_Controller": GRAGSimpleController
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRAG_Simple_Controller": "🎛️ GRAG Simple Controller v3.0"
}
