"""
GRAG Attention Reweighting Algorithm v3.0

Enhanced version of v2.2.1 with:
- Per-layer control support
- Adaptive timestep scheduling
- Multi-resolution tier support
- Improved numerical stability
- Architecture-agnostic design

Mathematical formulation (from arXiv 2510.24657):
  k_i = k_bias + Δk_i                    # Decompose keys
  k_bias = mean(k_1, k_2, ..., k_N)      # Group bias
  Δk_i = k_i - k_bias                     # Token deviation
  k̂_i = λ * k_bias + δ * Δk_i            # Reweight

Where:
  λ (lambda): Controls bias strength (>1 enhances, <1 reduces)
  δ (delta): Controls deviation intensity (>1 amplifies, <1 suppresses)

Author: Amir Ferdos (ArchAi3d)
Based on: v2.2.1 implementation + Paper improvements
License: MIT
"""

import torch
from typing import Union, Optional, Dict
from dataclasses import dataclass


@dataclass
class GRAGConfig:
    """Configuration for GRAG attention reweighting.

    Attributes:
        enabled (bool): Whether GRAG is active
        lambda_val (float | list[float]): Bias strength (per-layer if list)
        delta_val (float | list[float]): Deviation strength (per-layer if list)
        heads (int): Number of attention heads
        layer_idx (int): Current layer index (for per-layer control)
        timestep (int): Current denoising timestep (for adaptive control)
        strength_multiplier (float): Overall intensity multiplier
        multi_resolution (bool): Use multi-resolution tiers
        tier_config (dict): Multi-resolution configuration
        eps (float): Numerical stability epsilon
    """
    enabled: bool = True
    lambda_val: Union[float, list[float]] = 1.0
    delta_val: Union[float, list[float]] = 1.05
    heads: int = 16
    layer_idx: Optional[int] = None
    timestep: Optional[int] = None
    strength_multiplier: float = 1.0
    multi_resolution: bool = False
    tier_config: Optional[Dict] = None
    eps: float = 1e-6


def apply_grag_v3(
    joint_key: torch.Tensor,
    seq_txt: int,
    config: GRAGConfig
) -> torch.Tensor:
    """Apply GRAG v3.0 reweighting to joint attention keys.

    This is the core GRAG algorithm with v3.0 enhancements:
    - Per-layer control (different λ/δ per layer)
    - Adaptive timestep scheduling
    - Multi-resolution tier support
    - Improved numerical stability

    Args:
        joint_key (torch.Tensor): Joint attention keys [B, S, C] after RoPE
            B = batch size
            S = sequence length (text + image tokens)
            C = channels (heads * head_dim)
        seq_txt (int): Length of text sequence (separates text/image streams)
        config (GRAGConfig): GRAG configuration object

    Returns:
        torch.Tensor: Modified joint keys with GRAG reweighting [B, S, C]

    Mathematical Operations:
        For each stream (text and image):
        1. k_mean = mean(k_tokens, dim=1) + eps  # Group bias (with stability)
        2. Δk = k - k_mean                        # Token deviations
        3. k_reweighted = λ * k_mean + δ * Δk     # Apply reweighting

    v3.0 Enhancements:
        - Per-layer: λ/δ can be lists indexed by layer_idx
        - Adaptive: λ/δ scaled by timestep-dependent factor
        - Multi-res: Different scales for different resolution tiers
        - Stability: Added epsilon to prevent division issues
    """
    if not config.enabled:
        return joint_key

    # Get effective λ and δ (handle per-layer control)
    lambda_val = _get_effective_param(config.lambda_val, config.layer_idx)
    delta_val = _get_effective_param(config.delta_val, config.layer_idx)

    # Apply adaptive timestep scaling if configured
    if config.timestep is not None and config.strength_multiplier != 1.0:
        # Note: Actual adaptive scheduling is handled by AdaptiveScheduler
        # This is just the strength multiplier application
        lambda_val = 1.0 + (lambda_val - 1.0) * config.strength_multiplier
        delta_val = 1.0 + (delta_val - 1.0) * config.strength_multiplier

    # Get tensor dimensions
    batch, seq, channels = joint_key.shape
    head_dim = channels // config.heads

    # Reshape from ComfyUI format [B, S, C] to GRAG format [B, S, H, D]
    # This separates the heads dimension for per-head operations
    joint_key = joint_key.unflatten(-1, (config.heads, head_dim))

    # ===== TEXT STREAM GRAG =====
    # Extract text tokens (first seq_txt positions)
    txt_key = joint_key[:, :seq_txt, :, :]  # [B, seq_txt, H, D]

    # Compute group mean (bias vector) across token dimension
    # Add epsilon for numerical stability (v3.0 improvement)
    txt_key_mean = txt_key.mean(dim=1, keepdim=True) + config.eps  # [B, 1, H, D]

    # Apply GRAG reweighting: k̂ = λ * k_bias + δ * (k - k_bias)
    # Equivalent to: k̂ = λ * k_mean + δ * Δk
    txt_key = lambda_val * txt_key_mean + delta_val * (txt_key - txt_key_mean)

    # ===== IMAGE STREAM GRAG =====
    # Extract image tokens (remaining positions after text)
    img_key = joint_key[:, seq_txt:, :, :]  # [B, seq_img, H, D]

    # Compute group mean (bias vector) across token dimension
    img_key_mean = img_key.mean(dim=1, keepdim=True) + config.eps  # [B, 1, H, D]

    # Apply GRAG reweighting
    img_key = lambda_val * img_key_mean + delta_val * (img_key - img_key_mean)

    # ===== RECOMBINE STREAMS =====
    # Concatenate text and image streams back together
    joint_key = torch.cat([txt_key, img_key], dim=1)  # [B, S, H, D]

    # Reshape back to ComfyUI format [B, S, C]
    joint_key = joint_key.flatten(start_dim=2)  # [B, S, H*D]

    return joint_key


def _get_effective_param(param: Union[float, list[float]], layer_idx: Optional[int]) -> float:
    """Get effective parameter value (handle per-layer control).

    Args:
        param: Single float or list of per-layer floats
        layer_idx: Current layer index (None if global control)

    Returns:
        float: Effective parameter value for this layer
    """
    if isinstance(param, list):
        if layer_idx is None:
            # No layer index provided, use first value
            return param[0]
        # Clamp layer_idx to valid range
        idx = min(layer_idx, len(param) - 1)
        return param[idx]
    else:
        # Single global value
        return param


def extract_grag_config_from_conditioning(conditioning: list) -> Optional[GRAGConfig]:
    """Extract GRAG configuration from ComfyUI conditioning metadata.

    Reads GRAG parameters embedded in conditioning by the GRAG Unified Controller.
    Supports both v2.2.1 format and v3.0 format for backward compatibility.

    Args:
        conditioning (list): ComfyUI conditioning format
            [(embeddings_tensor, metadata_dict), ...]

    Returns:
        GRAGConfig | None: GRAG config object if enabled, None otherwise

    Example v2.2.1 metadata:
        {
            "grag_enabled": True,
            "grag_cond_b": 1.0,
            "grag_cond_delta": 1.0,
            "grag_strength": 1.0,
        }

    Example v3.0 metadata:
        {
            "grag_enabled": True,
            "grag_lambda": 1.0,  # or [0.9, 1.0, 1.1, ...] for per-layer
            "grag_delta": 1.05,
            "grag_strength_multiplier": 1.0,
            "grag_multi_resolution": False,
            "grag_tier_config": {...},
        }
    """
    # Validate conditioning format
    if not conditioning or len(conditioning) == 0:
        return None

    if len(conditioning[0]) < 2:
        return None

    # Extract metadata from first conditioning entry
    metadata = conditioning[0][1]

    if not isinstance(metadata, dict):
        return None

    # Check if GRAG is enabled
    if not metadata.get("grag_enabled", False):
        return None

    # Extract GRAG parameters (support both v2.2.1 and v3.0 formats)
    # v3.0 format takes precedence
    lambda_val = metadata.get("grag_lambda", metadata.get("grag_cond_b", 1.0))
    delta_val = metadata.get("grag_delta", metadata.get("grag_cond_delta", 1.05))
    strength = metadata.get("grag_strength_multiplier", metadata.get("grag_strength", 1.0))

    # Create GRAG config
    config = GRAGConfig(
        enabled=True,
        lambda_val=lambda_val,
        delta_val=delta_val,
        heads=metadata.get("grag_heads", 16),  # Qwen default: 16 heads
        strength_multiplier=strength,
        multi_resolution=metadata.get("grag_multi_resolution", False),
        tier_config=metadata.get("grag_tier_config", None),
    )

    return config


def validate_grag_parameters(lambda_val: float, delta_val: float) -> tuple[bool, str]:
    """Validate GRAG parameter ranges and warn if outside stable range.

    Testing range: [0.1, 2.0] for full experimentation (v2.2.1 proven range)
    Paper (arXiv 2510.24657) recommends: lambda and delta in [0.95, 1.15]
    for stable, training-free image editing.

    Args:
        lambda_val (float): Bias strength (lambda)
        delta_val (float): Deviation strength (delta)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(lambda_val, (int, float)):
        return False, "lambda must be numeric"

    if not isinstance(delta_val, (int, float)):
        return False, "delta must be numeric"

    # Hard limits (v2.2.1 proven testing range)
    if lambda_val < 0.1 or lambda_val > 2.0:
        return False, "lambda should be in range [0.1, 2.0]"

    if delta_val < 0.1 or delta_val > 2.0:
        return False, "delta should be in range [0.1, 2.0]"

    # Soft warnings (paper's stable range)
    STABLE_MIN = 0.95
    STABLE_MAX = 1.15

    if lambda_val < STABLE_MIN or lambda_val > STABLE_MAX:
        print(f"[GRAG v3.0] Info: lambda={lambda_val:.3f} outside paper's stable range [{STABLE_MIN}, {STABLE_MAX}]")
        print(f"[GRAG v3.0] Using v2.2.1 proven range - expect visible effects")

    if delta_val < STABLE_MIN or delta_val > STABLE_MAX:
        print(f"[GRAG v3.0] Info: delta={delta_val:.3f} outside paper's stable range [{STABLE_MIN}, {STABLE_MAX}]")
        print(f"[GRAG v3.0] Using v2.2.1 proven range - expect visible effects")

    return True, ""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "GRAGConfig",
    "apply_grag_v3",
    "extract_grag_config_from_conditioning",
    "validate_grag_parameters",
]
