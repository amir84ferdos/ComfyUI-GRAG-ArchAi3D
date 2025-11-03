"""
Adaptive Timestep GRAG Control System

Adjusts GRAG intensity based on denoising timestep, enabling different
editing strengths at different stages of generation.

Key insight: Different denoising stages have different sensitivities:
- Early (noisy): Forming structure → preserve with gentle GRAG
- Middle (forming): Establishing semantics → moderate GRAG
- Late (refining): Adding details → stronger GRAG

By varying GRAG intensity per timestep, we can:
- Preserve structural coherence in early steps
- Guide semantic transformations in middle steps
- Enhance fine details in final steps

Author: Amir Ferdos (ArchAi3d)
License: MIT
"""

import math
from typing import Literal


class AdaptiveScheduler:
    """Manages timestep-dependent GRAG parameter adjustment.

    Provides various scheduling strategies for varying GRAG intensity
    throughout the denoising process.
    """

    def __init__(self):
        pass

    def get_schedule(
        self,
        total_steps: int,
        schedule_type: Literal["linear", "exponential", "sine", "cosine", "custom"] = "linear",
        lambda_base: float = 1.0,
        delta_base: float = 1.05,
        multiplier_start: float = 0.8,
        multiplier_end: float = 1.5,
        custom_multipliers: list[float] | None = None,
    ) -> list[tuple[float, float]]:
        """Generate (λ, δ) schedule for each timestep.

        Args:
            total_steps: Total number of denoising steps
            schedule_type: Scheduling strategy
                - "linear": Linear increase from start to end
                - "exponential": Slow start, rapid increase
                - "sine": Smooth S-curve transition
                - "cosine": Inverted cosine curve
                - "custom": User-specified multipliers
            lambda_base: Base λ value (before multiplier)
            delta_base: Base δ value (before multiplier)
            multiplier_start: Starting multiplier (typically <1.0 for gentle start)
            multiplier_end: Ending multiplier (typically >1.0 for strong finish)
            custom_multipliers: Custom per-step multipliers (for schedule_type="custom")

        Returns:
            list: [(λ, δ), ...] for each timestep

        Schedule Details:

        **Linear** - Steady increase:
        ```
        Step 0:     multiplier=0.8 → λ=0.8, δ=0.84   (gentle)
        Step 10:    multiplier=1.15 → λ=1.15, δ=1.21 (moderate)
        Step 20:    multiplier=1.5 → λ=1.5, δ=1.58   (strong)
        ```

        **Exponential** - Slow start, rapid end:
        ```
        Step 0-10:  multiplier≈0.8-0.9   (very gradual)
        Step 10-15: multiplier≈0.9-1.2   (accelerating)
        Step 15-20: multiplier≈1.2-1.5   (rapid increase)
        ```

        **Sine** - Smooth S-curve:
        ```
        Step 0-5:   multiplier≈0.8-0.9   (gentle start)
        Step 5-15:  multiplier≈0.9-1.4   (smooth ramp)
        Step 15-20: multiplier≈1.4-1.5   (gentle finish)
        ```

        **Cosine** - Inverted cosine (common in diffusion):
        ```
        Follows cosine annealing schedule used in many diffusion models
        Smooth decrease in noise → smooth increase in GRAG strength
        ```
        """
        if schedule_type == "custom":
            if custom_multipliers is None:
                raise ValueError("custom schedule requires custom_multipliers")
            multipliers = self._pad_or_truncate(custom_multipliers, total_steps)

        elif schedule_type == "linear":
            multipliers = self._linear_schedule(multiplier_start, multiplier_end, total_steps)

        elif schedule_type == "exponential":
            multipliers = self._exponential_schedule(multiplier_start, multiplier_end, total_steps)

        elif schedule_type == "sine":
            multipliers = self._sine_schedule(multiplier_start, multiplier_end, total_steps)

        elif schedule_type == "cosine":
            multipliers = self._cosine_schedule(multiplier_start, multiplier_end, total_steps)

        else:
            raise ValueError(f"Unknown schedule_type: {schedule_type}")

        # Apply multipliers to base λ and δ
        schedule = []
        for mult in multipliers:
            # Scale around 1.0: mult=0.8 → λ=0.8, mult=1.5 → λ=1.5
            lambda_val = 1.0 + (lambda_base - 1.0) * mult
            delta_val = 1.0 + (delta_base - 1.0) * mult
            schedule.append((lambda_val, delta_val))

        return schedule

    def _linear_schedule(self, start: float, end: float, n: int) -> list[float]:
        """Linear schedule from start to end."""
        if n == 1:
            return [(start + end) / 2]

        step = (end - start) / (n - 1)
        return [start + i * step for i in range(n)]

    def _exponential_schedule(self, start: float, end: float, n: int) -> list[float]:
        """Exponential schedule (slow start, rapid increase).

        Uses exponential curve: y = start * (end/start)^(t^2)
        where t ∈ [0, 1]
        """
        if n == 1:
            return [(start + end) / 2]

        values = []
        for i in range(n):
            # Normalize position to [0, 1]
            t = i / (n - 1)
            # Exponential curve with quadratic exponent
            value = start * math.pow(end / start, t * t)
            values.append(value)

        return values

    def _sine_schedule(self, start: float, end: float, n: int) -> list[float]:
        """Sine schedule (smooth S-curve).

        Uses sine function: y = start + (end - start) * sin(π*t/2)
        where t ∈ [0, 1]
        """
        if n == 1:
            return [(start + end) / 2]

        values = []
        for i in range(n):
            # Normalize position to [0, 1]
            t = i / (n - 1)
            # Sine S-curve (0 → 1)
            sine_factor = math.sin(math.pi * t / 2)
            value = start + (end - start) * sine_factor
            values.append(value)

        return values

    def _cosine_schedule(self, start: float, end: float, n: int) -> list[float]:
        """Cosine schedule (inverted cosine annealing).

        Uses cosine function: y = start + (end - start) * (1 - cos(π*t)) / 2
        where t ∈ [0, 1]

        This matches the cosine annealing schedule commonly used in diffusion models.
        """
        if n == 1:
            return [(start + end) / 2]

        values = []
        for i in range(n):
            # Normalize position to [0, 1]
            t = i / (n - 1)
            # Cosine annealing curve
            cosine_factor = (1 - math.cos(math.pi * t)) / 2
            value = start + (end - start) * cosine_factor
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
# PRESET SCHEDULES
# ============================================================================

PRESET_SCHEDULES = {
    "gentle_to_strong": {
        "name": "Gentle to Strong",
        "schedule_type": "linear",
        "multiplier_start": 0.8,
        "multiplier_end": 1.5,
        "description": "Steady linear increase from gentle to strong",
        "use_case": "General editing, predictable progression"
    },
    "conservative": {
        "name": "Conservative",
        "schedule_type": "exponential",
        "multiplier_start": 0.9,
        "multiplier_end": 1.2,
        "description": "Slow start, moderate finish. Preserves structure.",
        "use_case": "Structural preservation, subtle edits"
    },
    "aggressive": {
        "name": "Aggressive",
        "schedule_type": "exponential",
        "multiplier_start": 0.8,
        "multiplier_end": 1.8,
        "description": "Slow start, very strong finish. Maximum transformation.",
        "use_case": "Complete redesigns, dramatic changes"
    },
    "smooth_transition": {
        "name": "Smooth Transition",
        "schedule_type": "sine",
        "multiplier_start": 0.85,
        "multiplier_end": 1.4,
        "description": "Smooth S-curve transition. Balanced and natural.",
        "use_case": "Natural edits, smooth transformations"
    },
    "diffusion_aligned": {
        "name": "Diffusion Aligned",
        "schedule_type": "cosine",
        "multiplier_start": 0.8,
        "multiplier_end": 1.5,
        "description": "Matches diffusion model's cosine noise schedule.",
        "use_case": "Optimal alignment with model behavior"
    },
}


def get_preset_schedule(preset_name: str) -> dict:
    """Get preset adaptive schedule configuration.

    Args:
        preset_name: Name of preset schedule

    Returns:
        dict: Schedule configuration

    Available presets:
        - "gentle_to_strong": Linear 0.8 → 1.5
        - "conservative": Exponential 0.9 → 1.2 (structure preservation)
        - "aggressive": Exponential 0.8 → 1.8 (maximum transformation)
        - "smooth_transition": Sine 0.85 → 1.4 (natural edits)
        - "diffusion_aligned": Cosine 0.8 → 1.5 (optimal alignment)
    """
    return PRESET_SCHEDULES.get(preset_name, PRESET_SCHEDULES["smooth_transition"])


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "AdaptiveScheduler",
    "PRESET_SCHEDULES",
    "get_preset_schedule",
]
