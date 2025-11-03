"""
Per-Layer GRAG Control System

Allows different λ/δ parameters for each transformer block, enabling
precise control over where GRAG effects are applied.

Key insight: Different layers have different roles:
- Early layers: Encode low-level features (edges, textures)
- Middle layers: Encode semantic content (objects, composition)
- Late layers: Encode fine details (materials, lighting)

By varying GRAG intensity per layer, we can:
- Preserve structure (lower λ/δ in early layers)
- Transform semantics (higher λ/δ in middle layers)
- Enhance details (moderate λ/δ in late layers)

Author: Amir Ferdos (ArchAi3d)
License: MIT
"""

import math
from typing import Literal


class LayerSpecificController:
    """Manages per-layer λ/δ parameters for GRAG.

    Provides various strategies for distributing GRAG intensity
    across transformer layers.
    """

    def __init__(self):
        pass

    def compute_layer_params(
        self,
        total_layers: int,
        strategy: Literal["linear", "u_shaped", "bell_curve", "custom"] = "linear",
        lambda_start: float = 0.9,
        lambda_end: float = 1.3,
        delta_start: float = 0.9,
        delta_end: float = 1.3,
        custom_lambda: list[float] | None = None,
        custom_delta: list[float] | None = None,
    ) -> tuple[list[float], list[float]]:
        """Compute per-layer λ and δ values.

        Args:
            total_layers: Number of transformer layers in model
            strategy: Distribution strategy
                - "linear": Gradual increase from start to end
                - "u_shaped": High at start/end, low in middle
                - "bell_curve": Low at start/end, high in middle
                - "custom": User-specified values
            lambda_start: Starting λ value (for linear/u_shaped/bell_curve)
            lambda_end: Ending λ value (for linear/u_shaped/bell_curve)
            delta_start: Starting δ value
            delta_end: Ending δ value
            custom_lambda: Custom per-layer λ values (for strategy="custom")
            custom_delta: Custom per-layer δ values (for strategy="custom")

        Returns:
            tuple: (lambda_values, delta_values) as lists of length total_layers

        Strategy Details:

        **Linear** - Gradual strength increase:
        ```
        Early (0-8):    λ=0.9, δ=0.9   (preserve structure)
        Middle (9-16):  λ=1.1, δ=1.1   (moderate editing)
        Late (17-24):   λ=1.3, δ=1.3   (enhance details)
        ```

        **U-Shaped** - Strong at extremes:
        ```
        Early (0-8):    λ=1.3, δ=1.3   (strong low-level edits)
        Middle (9-16):  λ=0.9, δ=0.9   (preserve semantics)
        Late (17-24):   λ=1.3, δ=1.3   (strong detail edits)
        ```

        **Bell-Curve** - Focus on middle layers:
        ```
        Early (0-8):    λ=0.9, δ=0.9   (preserve structure)
        Middle (9-16):  λ=1.4, δ=1.4   (strong semantic edits)
        Late (17-24):   λ=0.9, δ=0.9   (preserve details)
        ```
        """
        if strategy == "custom":
            # Use custom-specified values
            if custom_lambda is None or custom_delta is None:
                raise ValueError("custom strategy requires custom_lambda and custom_delta")

            # Pad or truncate to match total_layers
            lambda_values = self._pad_or_truncate(custom_lambda, total_layers)
            delta_values = self._pad_or_truncate(custom_delta, total_layers)

        elif strategy == "linear":
            # Linear interpolation from start to end
            lambda_values = self._linear_interpolate(lambda_start, lambda_end, total_layers)
            delta_values = self._linear_interpolate(delta_start, delta_end, total_layers)

        elif strategy == "u_shaped":
            # U-shaped curve (high → low → high)
            lambda_values = self._u_shaped_curve(lambda_start, lambda_end, total_layers)
            delta_values = self._u_shaped_curve(delta_start, delta_end, total_layers)

        elif strategy == "bell_curve":
            # Bell curve (low → high → low)
            lambda_values = self._bell_curve(lambda_start, lambda_end, total_layers)
            delta_values = self._bell_curve(delta_start, delta_end, total_layers)

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return lambda_values, delta_values

    def _linear_interpolate(self, start: float, end: float, n: int) -> list[float]:
        """Linear interpolation from start to end over n steps."""
        if n == 1:
            return [(start + end) / 2]

        step = (end - start) / (n - 1)
        return [start + i * step for i in range(n)]

    def _u_shaped_curve(self, start: float, end: float, n: int) -> list[float]:
        """U-shaped curve (high at start/end, low in middle).

        Uses cosine interpolation for smooth transitions:
        - Layer 0: start value (high)
        - Layer n/2: minimum value (low)
        - Layer n-1: end value (high)
        """
        if n == 1:
            return [(start + end) / 2]

        # Minimum value at middle
        mid_value = min(start, end)
        max_value = max(start, end)

        values = []
        for i in range(n):
            # Normalize position to [0, 1]
            t = i / (n - 1)
            # Cosine curve: 1 → 0 → 1
            cosine_factor = (1 + math.cos(math.pi * t)) / 2
            # Interpolate between mid and max
            value = mid_value + (max_value - mid_value) * cosine_factor
            values.append(value)

        return values

    def _bell_curve(self, start: float, end: float, n: int) -> list[float]:
        """Bell curve (low at start/end, high in middle).

        Uses sine interpolation for smooth transitions:
        - Layer 0: start value (low)
        - Layer n/2: maximum value (high)
        - Layer n-1: end value (low)
        """
        if n == 1:
            return [(start + end) / 2]

        # Maximum value at middle
        max_value = max(start, end)
        min_value = min(start, end)

        values = []
        for i in range(n):
            # Normalize position to [0, 1]
            t = i / (n - 1)
            # Sine curve: 0 → 1 → 0
            sine_factor = math.sin(math.pi * t)
            # Interpolate between min and max
            value = min_value + (max_value - min_value) * sine_factor
            values.append(value)

        return values

    def _pad_or_truncate(self, values: list[float], target_length: int) -> list[float]:
        """Pad (repeat last value) or truncate list to target length."""
        if len(values) == target_length:
            return values
        elif len(values) < target_length:
            # Pad by repeating last value
            return values + [values[-1]] * (target_length - len(values))
        else:
            # Truncate
            return values[:target_length]


# ============================================================================
# PRESET LAYER STRATEGIES
# ============================================================================

PRESET_STRATEGIES = {
    "structure_preserving": {
        "name": "Structure Preserving",
        "strategy": "linear",
        "lambda_start": 0.9,
        "lambda_end": 1.2,
        "delta_start": 0.9,
        "delta_end": 1.3,
        "description": "Gentle edits early, stronger late. Preserves structure while transforming details.",
        "use_case": "Clean room workflow, architectural edits"
    },
    "semantic_focused": {
        "name": "Semantic Focused",
        "strategy": "bell_curve",
        "lambda_start": 0.9,
        "lambda_end": 0.9,
        "delta_start": 1.0,
        "delta_end": 1.0,
        "description": "Strong edits in middle layers (semantics), preserve structure and details.",
        "use_case": "Style transfer, object replacement"
    },
    "detail_enhancer": {
        "name": "Detail Enhancer",
        "strategy": "u_shaped",
        "lambda_start": 1.3,
        "lambda_end": 1.3,
        "delta_start": 1.3,
        "delta_end": 1.3,
        "description": "Strong edits at start/end, preserve middle semantics.",
        "use_case": "Material changes, texture enhancement"
    },
    "balanced_progressive": {
        "name": "Balanced Progressive",
        "strategy": "linear",
        "lambda_start": 1.0,
        "lambda_end": 1.3,
        "delta_start": 1.0,
        "delta_end": 1.3,
        "description": "Gradual increase from neutral to strong. Balanced approach.",
        "use_case": "General editing, testing GRAG effects"
    },
}


def get_preset_strategy(preset_name: str) -> dict:
    """Get preset layer strategy configuration.

    Args:
        preset_name: Name of preset strategy

    Returns:
        dict: Strategy configuration

    Available presets:
        - "structure_preserving": Gentle → Strong (preserve structure)
        - "semantic_focused": Low → High → Low (focus on semantics)
        - "detail_enhancer": High → Low → High (enhance details)
        - "balanced_progressive": Neutral → Strong (general use)
    """
    return PRESET_STRATEGIES.get(preset_name, PRESET_STRATEGIES["balanced_progressive"])


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "LayerSpecificController",
    "PRESET_STRATEGIES",
    "get_preset_strategy",
]
