"""
GRAG Unified Controller Node v3.0

Main interface node for GRAG attention control with progressive complexity:
- Simple Mode: Single global λ/δ with presets
- Advanced Mode: Per-layer control
- Expert Mode: Adaptive timestep + Multi-resolution

This node replaces v2.2.1's GRAG Modifier with enhanced capabilities.

Author: Amir Ferdos (ArchAi3d)
Email: Amir84ferdos@gmail.com
License: MIT
"""

import copy

# Use relative imports for package structure
from ..core.preset_loader import get_preset_loader
from ..core.per_layer_control import LayerSpecificController, PRESET_STRATEGIES
from ..core.adaptive_control import AdaptiveScheduler, PRESET_SCHEDULES
from ..core.multi_resolution import MultiResolutionController, PRESET_TIER_CONFIGS


class GRAGUnifiedController:
    """GRAG Unified Controller - Main interface for GRAG attention control.

    Progressive complexity modes:
    - Simple: Preset-based control (beginner-friendly)
    - Advanced: Per-layer λ/δ control (precision editing)
    - Expert: Adaptive timestep + Multi-resolution (maximum control)

    Backward compatible with v2.2.1 workflows.

    Version: 3.0.0
    """

    def __init__(self):
        self.preset_loader = get_preset_loader()
        self.layer_controller = LayerSpecificController()
        self.adaptive_scheduler = AdaptiveScheduler()
        self.multi_res_controller = MultiResolutionController()

    @classmethod
    def INPUT_TYPES(cls):
        # Load preset names dynamically
        preset_loader = get_preset_loader()
        preset_names = preset_loader.get_all_preset_names()

        # Per-layer strategy names
        layer_strategy_names = list(PRESET_STRATEGIES.keys()) + ["custom"]

        # Adaptive schedule names
        adaptive_schedule_names = list(PRESET_SCHEDULES.keys()) + ["custom"]

        # Multi-resolution tier preset names
        tier_preset_names = list(PRESET_TIER_CONFIGS.keys()) + ["custom"]

        return {
            "required": {
                # Input conditioning from any encoder
                "conditioning": ("CONDITIONING", {
                    "tooltip": "Conditioning from any encoder (Qwen, Flux, SD3, etc.)"
                }),

                # Main enable/disable toggle
                "enable_grag": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable GRAG attention guidance (passthrough if disabled)"
                }),

                # Control mode selector
                "control_mode": (["simple", "advanced", "expert"], {
                    "default": "simple",
                    "tooltip": "Simple: Presets only | Advanced: Per-layer | Expert: Adaptive + Multi-res"
                }),

                # === SIMPLE MODE ===
                # Preset selector (all 54 presets)
                "preset": (preset_names, {
                    "default": preset_names[0] if preset_names else "Custom",
                    "tooltip": "Choose preset or 'Custom' for manual control (54 presets available)"
                }),

                # Manual parameters (active when preset="Custom" or advanced/expert modes)
                "lambda_global": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Lambda (bias strength) - 1.0=neutral, >1=enhance, <1=reduce"
                }),
                "delta_global": ("FLOAT", {
                    "default": 1.05,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Delta (deviation intensity) - 1.0=neutral, >1=amplify, <1=suppress"
                }),

                # === ADVANCED MODE (Per-Layer) ===
                "per_layer_enabled": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable per-layer control (different λ/δ per transformer block)"
                }),
                "layer_strategy": (layer_strategy_names, {
                    "default": "structure_preserving",
                    "tooltip": "Per-layer distribution strategy"
                }),
                "lambda_start": ("FLOAT", {
                    "default": 0.9,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Starting λ for early layers"
                }),
                "lambda_end": ("FLOAT", {
                    "default": 1.3,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Ending λ for late layers"
                }),
                "delta_start": ("FLOAT", {
                    "default": 0.9,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Starting δ for early layers"
                }),
                "delta_end": ("FLOAT", {
                    "default": 1.3,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Ending δ for late layers"
                }),
                "total_layers": ("INT", {
                    "default": 60,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "Total transformer layers in model (Qwen: 60)"
                }),

                # === EXPERT MODE (Adaptive Timestep) ===
                "adaptive_enabled": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable adaptive timestep scheduling (vary strength during denoising)"
                }),
                "adaptive_schedule": (adaptive_schedule_names, {
                    "default": "smooth_transition",
                    "tooltip": "Timestep-dependent schedule type"
                }),
                "multiplier_start": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Starting multiplier (early denoising steps)"
                }),
                "multiplier_end": ("FLOAT", {
                    "default": 1.5,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Ending multiplier (late denoising steps)"
                }),

                # === EXPERT MODE (Multi-Resolution) ===
                "multi_resolution_enabled": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable multi-resolution tiers (paper's 2-tier system)"
                }),
                "tier_preset": (tier_preset_names, {
                    "default": "v221_visible",
                    "tooltip": "Multi-resolution tier preset"
                }),
                "tier1_resolution": ("INT", {
                    "default": 512,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                    "tooltip": "Tier 1 resolution (coarse structure)"
                }),
                "tier1_lambda": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Tier 1 λ (typically 1.0 for stability)"
                }),
                "tier1_delta": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Tier 1 δ (typically 1.0 for stability)"
                }),
                "tier2_resolution": ("INT", {
                    "default": 4096,
                    "min": 1024,
                    "max": 8192,
                    "step": 64,
                    "tooltip": "Tier 2 resolution (fine details)"
                }),
                "tier2_lambda": ("FLOAT", {
                    "default": 1.3,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Tier 2 λ (custom editing strength)"
                }),
                "tier2_delta": ("FLOAT", {
                    "default": 1.3,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Tier 2 δ (custom editing strength)"
                }),

                # Common parameters
                "strength_multiplier": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Overall GRAG intensity multiplier (stored, not currently applied)"
                }),
            }
        }

    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    FUNCTION = "apply_grag"
    CATEGORY = "GRAG/v3.0"

    def apply_grag(
        self,
        conditioning,
        enable_grag,
        control_mode,
        preset,
        lambda_global,
        delta_global,
        per_layer_enabled,
        layer_strategy,
        lambda_start,
        lambda_end,
        delta_start,
        delta_end,
        total_layers,
        adaptive_enabled,
        adaptive_schedule,
        multiplier_start,
        multiplier_end,
        multi_resolution_enabled,
        tier_preset,
        tier1_resolution,
        tier1_lambda,
        tier1_delta,
        tier2_resolution,
        tier2_lambda,
        tier2_delta,
        strength_multiplier,
    ):
        """Apply GRAG configuration to conditioning.

        This node prepares GRAG metadata that will be used by GRAG Advanced Sampler.

        Returns:
            tuple: (modified_conditioning,)
        """
        # Passthrough mode: GRAG disabled
        if not enable_grag:
            print("[GRAG v3.0] GRAG disabled - passthrough mode")
            return (conditioning,)

        # === SIMPLE MODE: Use Preset ===
        if control_mode == "simple" and preset != "Custom":
            preset_config = self.preset_loader.get_preset_by_name(preset)
            lambda_val = preset_config.get("lambda", 1.0)
            delta_val = preset_config.get("delta", 1.05)
            strength = preset_config.get("strength", 1.0)

            print(f"[GRAG v3.0] Simple Mode - Preset: {preset}")
            print(f"[GRAG v3.0] Parameters: λ={lambda_val:.2f}, δ={delta_val:.2f}, strength={strength:.2f}")

        else:
            # Use manual parameters
            lambda_val = lambda_global
            delta_val = delta_global
            strength = strength_multiplier

            print(f"[GRAG v3.0] {control_mode.capitalize()} Mode - Custom parameters")
            print(f"[GRAG v3.0] Global: λ={lambda_val:.2f}, δ={delta_val:.2f}")

        # === ADVANCED MODE: Per-Layer Control ===
        per_layer_lambda = None
        per_layer_delta = None

        if control_mode in ["advanced", "expert"] and per_layer_enabled:
            # Load preset strategy if not custom
            if layer_strategy != "custom" and layer_strategy in PRESET_STRATEGIES:
                strategy_config = PRESET_STRATEGIES[layer_strategy]
                lambda_start = strategy_config["lambda_start"]
                lambda_end = strategy_config["lambda_end"]
                delta_start = strategy_config["delta_start"]
                delta_end = strategy_config["delta_end"]
                strategy_type = strategy_config["strategy"]
            else:
                strategy_type = "linear"  # Default for custom

            # Compute per-layer values
            per_layer_lambda, per_layer_delta = self.layer_controller.compute_layer_params(
                total_layers=total_layers,
                strategy=strategy_type,
                lambda_start=lambda_start,
                lambda_end=lambda_end,
                delta_start=delta_start,
                delta_end=delta_end,
            )

            print(f"[GRAG v3.0] Per-layer control enabled: {layer_strategy} strategy")
            print(f"[GRAG v3.0] λ range: {min(per_layer_lambda):.2f}-{max(per_layer_lambda):.2f}")
            print(f"[GRAG v3.0] δ range: {min(per_layer_delta):.2f}-{max(per_layer_delta):.2f}")

            # Override lambda_val and delta_val with lists
            lambda_val = per_layer_lambda
            delta_val = per_layer_delta

        # === EXPERT MODE: Adaptive Timestep ===
        adaptive_schedule_data = None

        if control_mode == "expert" and adaptive_enabled:
            # Load preset schedule if not custom
            if adaptive_schedule != "custom" and adaptive_schedule in PRESET_SCHEDULES:
                schedule_config = PRESET_SCHEDULES[adaptive_schedule]
                multiplier_start = schedule_config["multiplier_start"]
                multiplier_end = schedule_config["multiplier_end"]
                schedule_type = schedule_config["schedule_type"]
            else:
                schedule_type = "linear"  # Default for custom

            # Generate schedule
            # Note: We don't know total_steps yet, sampler will handle this
            adaptive_schedule_data = {
                "enabled": True,
                "schedule_type": schedule_type,
                "multiplier_start": multiplier_start,
                "multiplier_end": multiplier_end,
                "lambda_base": lambda_global,  # Use global as base for adaptive
                "delta_base": delta_global,
            }

            print(f"[GRAG v3.0] Adaptive scheduling enabled: {adaptive_schedule}")
            print(f"[GRAG v3.0] Multiplier range: {multiplier_start:.2f}-{multiplier_end:.2f}")

        # === EXPERT MODE: Multi-Resolution Tiers ===
        tier_config = None

        if control_mode == "expert" and multi_resolution_enabled:
            # Load preset tier config if not custom
            if tier_preset != "custom" and tier_preset in PRESET_TIER_CONFIGS:
                tier_cfg = PRESET_TIER_CONFIGS[tier_preset]
                tier1_resolution = tier_cfg["tier1_resolution"]
                tier1_lambda = tier_cfg["tier1_lambda"]
                tier1_delta = tier_cfg["tier1_delta"]
                tier2_resolution = tier_cfg["tier2_resolution"]
                tier2_lambda = tier_cfg["tier2_lambda"]
                tier2_delta = tier_cfg["tier2_delta"]

            # Create tier configuration
            tier_config = self.multi_res_controller.create_tier_config(
                tier1_resolution=tier1_resolution,
                tier1_lambda=tier1_lambda,
                tier1_delta=tier1_delta,
                tier2_resolution=tier2_resolution,
                tier2_lambda=tier2_lambda,
                tier2_delta=tier2_delta,
            )

            print(f"[GRAG v3.0] Multi-resolution enabled: {tier_preset}")
            print(f"[GRAG v3.0] Tier 1: {tier1_resolution}px (λ={tier1_lambda:.2f}, δ={tier1_delta:.2f})")
            print(f"[GRAG v3.0] Tier 2: {tier2_resolution}px (λ={tier2_lambda:.2f}, δ={tier2_delta:.2f})")

        # === BUILD GRAG METADATA ===
        grag_cond = copy.deepcopy(conditioning)

        # Add GRAG configuration to conditioning metadata
        for i in range(len(grag_cond)):
            if len(grag_cond[i]) >= 2:
                # Get or create metadata dict
                metadata = grag_cond[i][1].copy() if isinstance(grag_cond[i][1], dict) else {}

                # v3.0 format (primary)
                metadata['grag_enabled'] = True
                metadata['grag_lambda'] = lambda_val  # Can be float or list
                metadata['grag_delta'] = delta_val    # Can be float or list
                metadata['grag_strength_multiplier'] = strength

                # v2.2.1 backward compatibility
                metadata['grag_cond_b'] = lambda_val if not isinstance(lambda_val, list) else lambda_val[0]
                metadata['grag_cond_delta'] = delta_val if not isinstance(delta_val, list) else delta_val[0]
                metadata['grag_strength'] = strength

                # Advanced features
                if adaptive_schedule_data:
                    metadata['grag_adaptive_schedule'] = adaptive_schedule_data

                if tier_config:
                    metadata['grag_tier_config'] = tier_config
                    metadata['grag_multi_resolution'] = True

                # Store control mode for sampler
                metadata['grag_control_mode'] = control_mode

                # Update conditioning
                grag_cond[i] = (grag_cond[i][0], metadata)

        print(f"[GRAG v3.0] Configuration embedded in conditioning")
        print(f"[GRAG v3.0] Use 'GRAG Advanced Sampler' to apply effects")

        return (grag_cond,)


# ============================================================================
# COMFYUI NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "GRAG_Unified_Controller": GRAGUnifiedController
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRAG_Unified_Controller": "🎚️ GRAG Unified Controller v3.0"
}
