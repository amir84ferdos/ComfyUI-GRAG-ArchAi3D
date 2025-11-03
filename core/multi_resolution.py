"""
Multi-Resolution Tier GRAG Control System

Implements the paper's original 2-tier resolution system where different
GRAG parameters are applied based on feature resolution.

Key insight from paper (arXiv 2510.24657):
- Tier 1 (low-res, e.g., 512×512): Neutral λ=1.0, δ=1.0 (stable reference)
- Tier 2 (high-res, e.g., 4096×4096): Custom λ/δ (editing control)

This allows:
- Preserve coarse structure at low resolution
- Apply fine-grained edits at high resolution
- Better stability and control

Author: Amir Ferdos (ArchAi3d)
Based on: arXiv 2510.24657 Section 3.2
License: MIT
"""

from typing import Dict, Tuple


class MultiResolutionController:
    """Manages multi-resolution tier configuration for GRAG.

    Implements the paper's 2-tier system with customizable resolutions
    and parameters per tier.
    """

    def __init__(self):
        pass

    def create_tier_config(
        self,
        tier1_resolution: int = 512,
        tier1_lambda: float = 1.0,
        tier1_delta: float = 1.0,
        tier2_resolution: int = 4096,
        tier2_lambda: float = 1.0,
        tier2_delta: float = 1.05,
        num_steps: int = 60,
    ) -> Dict:
        """Create multi-resolution tier configuration.

        Args:
            tier1_resolution: Resolution for tier 1 (typically 512)
            tier1_lambda: Lambda for tier 1 (typically 1.0 for stability)
            tier1_delta: Delta for tier 1 (typically 1.0 for stability)
            tier2_resolution: Resolution for tier 2 (typically 4096)
            tier2_lambda: Lambda for tier 2 (custom editing strength)
            tier2_delta: Delta for tier 2 (custom editing strength)
            num_steps: Number of denoising steps

        Returns:
            dict: Multi-resolution configuration

        Paper's Recommended Values:
            Tier 1: 512×512, λ=1.0, δ=1.0 (stable reference, no GRAG)
            Tier 2: 4096×4096, λ=1.0-1.15, δ=1.0-1.15 (controlled editing)

        v2.2.1 Proven Values (for visible effects):
            Tier 1: 512×512, λ=0.8-1.0, δ=0.8-1.0 (optional gentle GRAG)
            Tier 2: 4096×4096, λ=0.8-1.5, δ=0.8-1.5 (strong visible effects)
        """
        tier_config = {
            "enabled": True,
            "num_tiers": 2,
            "tiers": [
                {
                    "resolution": tier1_resolution,
                    "lambda": tier1_lambda,
                    "delta": tier1_delta,
                    "description": f"Tier 1: {tier1_resolution}×{tier1_resolution} (structure)"
                },
                {
                    "resolution": tier2_resolution,
                    "lambda": tier2_lambda,
                    "delta": tier2_delta,
                    "description": f"Tier 2: {tier2_resolution}×{tier2_resolution} (details)"
                }
            ],
            "num_steps": num_steps,
        }

        return tier_config

    def get_tier_for_resolution(
        self,
        current_resolution: int,
        tier_config: Dict
    ) -> Tuple[float, float]:
        """Get appropriate λ/δ for current feature resolution.

        Args:
            current_resolution: Current feature map resolution (H or W)
            tier_config: Multi-resolution configuration

        Returns:
            tuple: (lambda, delta) for this resolution

        Resolution Matching Logic:
            - Find closest tier by resolution
            - If resolution < tier1: use tier1 parameters
            - If tier1 <= resolution < tier2: interpolate or use tier1
            - If resolution >= tier2: use tier2 parameters
        """
        if not tier_config.get("enabled", False):
            # Multi-resolution disabled, return tier 2 params (default editing)
            return tier_config["tiers"][1]["lambda"], tier_config["tiers"][1]["delta"]

        tiers = tier_config["tiers"]

        # Sort tiers by resolution
        sorted_tiers = sorted(tiers, key=lambda t: t["resolution"])

        # Find appropriate tier
        if current_resolution <= sorted_tiers[0]["resolution"]:
            # Below first tier, use first tier parameters
            tier = sorted_tiers[0]
        elif current_resolution >= sorted_tiers[-1]["resolution"]:
            # Above last tier, use last tier parameters
            tier = sorted_tiers[-1]
        else:
            # Between tiers, use closest tier
            # (Could implement interpolation here for smoother transitions)
            closest_tier = min(sorted_tiers, key=lambda t: abs(t["resolution"] - current_resolution))
            tier = closest_tier

        return tier["lambda"], tier["delta"]

    def build_grag_scale_list(
        self,
        tier_config: Dict
    ) -> list:
        """Build GRAG scale list for all inference steps.

        This creates the format used by the paper's implementation:
        [
            ((tier1_res, tier1_λ, tier1_δ), (tier2_res, tier2_λ, tier2_δ)),  # Step 1
            ((tier1_res, tier1_λ, tier1_δ), (tier2_res, tier2_λ, tier2_δ)),  # Step 2
            ...
        ]

        Args:
            tier_config: Multi-resolution configuration

        Returns:
            list: GRAG scale configuration for each step

        Note: This format is primarily for metadata storage.
              Actual per-layer application uses get_tier_for_resolution().
        """
        if not tier_config.get("enabled", False):
            return []

        tiers = tier_config["tiers"]
        num_steps = tier_config.get("num_steps", 60)

        # Build tier tuple format
        tier_tuple = tuple(
            (tier["resolution"], tier["lambda"], tier["delta"])
            for tier in tiers
        )

        # Repeat for all steps
        grag_scale = [tier_tuple] * num_steps

        return grag_scale


# ============================================================================
# PRESET TIER CONFIGURATIONS
# ============================================================================

PRESET_TIER_CONFIGS = {
    "paper_stable": {
        "name": "Paper: Stable (2-tier)",
        "tier1_resolution": 512,
        "tier1_lambda": 1.0,
        "tier1_delta": 1.0,
        "tier2_resolution": 4096,
        "tier2_lambda": 1.05,
        "tier2_delta": 1.10,
        "description": "Paper-recommended stable configuration",
        "use_case": "Validated by research, maximum stability"
    },
    "v221_visible": {
        "name": "v2.2.1: Visible Effects",
        "tier1_resolution": 512,
        "tier1_lambda": 0.9,
        "tier1_delta": 0.9,
        "tier2_resolution": 4096,
        "tier2_lambda": 1.3,
        "tier2_delta": 1.3,
        "description": "v2.2.1 proven range for visible effects",
        "use_case": "Clear transformations, strong edits"
    },
    "structure_preserving": {
        "name": "Structure Preserving",
        "tier1_resolution": 512,
        "tier1_lambda": 1.0,
        "tier1_delta": 1.0,
        "tier2_resolution": 4096,
        "tier2_lambda": 0.85,
        "tier2_delta": 1.15,
        "description": "Neutral coarse, gentle details",
        "use_case": "Window preservation, structural edits"
    },
    "detail_focused": {
        "name": "Detail Focused",
        "tier1_resolution": 512,
        "tier1_lambda": 1.0,
        "tier1_delta": 1.0,
        "tier2_resolution": 4096,
        "tier2_lambda": 1.5,
        "tier2_delta": 1.8,
        "description": "Neutral coarse, strong details",
        "use_case": "Material changes, texture enhancement"
    },
}


def get_preset_tier_config(preset_name: str) -> Dict:
    """Get preset multi-resolution tier configuration.

    Args:
        preset_name: Name of preset configuration

    Returns:
        dict: Tier configuration parameters

    Available presets:
        - "paper_stable": Paper's validated 2-tier (λ/δ in 1.0-1.15 range)
        - "v221_visible": v2.2.1 proven visible effects (λ/δ in 0.9-1.3 range)
        - "structure_preserving": Preserve structure, gentle details
        - "detail_focused": Neutral structure, strong detail edits
    """
    return PRESET_TIER_CONFIGS.get(preset_name, PRESET_TIER_CONFIGS["v221_visible"])


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "MultiResolutionController",
    "PRESET_TIER_CONFIGS",
    "get_preset_tier_config",
]
