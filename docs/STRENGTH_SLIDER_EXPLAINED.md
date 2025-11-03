# GRAG Simple Controller - Strength Slider Explained

## How the Strength Slider Works

The strength slider in the **🎛️ GRAG Simple Controller** now scales λ (lambda) and δ (delta) parameters **proportionally from neutral (1.0)** to give you intuitive control over effect intensity.

---

## The Math Behind It

### Neutral Point: λ=1.0, δ=1.0
When both λ and δ are exactly 1.0, the GRAG formula produces **NO change**:
```
k̂ = λ * k_mean + δ * (k - k_mean)
k̂ = 1.0 * k_mean + 1.0 * (k - k_mean)
k̂ = k_mean + k - k_mean
k̂ = k  (unchanged)
```

### Scaling Formula
Given a preset with `λ_base` and `δ_base`, the strength slider scales like this:

```python
# Calculate how far preset values are from neutral
lambda_deviation = lambda_base - 1.0
delta_deviation = delta_base - 1.0

# Scale deviations by strength slider
lambda_actual = 1.0 + (lambda_deviation × strength)
delta_actual = 1.0 + (delta_deviation × strength)
```

---

## Examples with "Paper: Balanced" Preset

**Preset base values:** λ=1.05, δ=1.10

### Strength = 0.0 (No Effect)
```
λ_deviation = 1.05 - 1.0 = 0.05
δ_deviation = 1.10 - 1.0 = 0.10

λ_actual = 1.0 + (0.05 × 0.0) = 1.000
δ_actual = 1.0 + (0.10 × 0.0) = 1.000
```
**Result:** No change to image (neutral)

### Strength = 0.1 (Minimal Effect)
```
λ_actual = 1.0 + (0.05 × 0.1) = 1.005
δ_actual = 1.0 + (0.10 × 0.1) = 1.010
```
**Result:** Very subtle changes, barely noticeable

### Strength = 0.5 (Half Effect)
```
λ_actual = 1.0 + (0.05 × 0.5) = 1.025
δ_actual = 1.0 + (0.10 × 0.5) = 1.050
```
**Result:** Gentle, visible changes

### Strength = 1.0 (Preset's Intended Effect) ⭐
```
λ_actual = 1.0 + (0.05 × 1.0) = 1.05
δ_actual = 1.0 + (0.10 × 1.0) = 1.10
```
**Result:** Balanced changes (preset's original values)

### Strength = 1.5 (Enhanced Effect)
```
λ_actual = 1.0 + (0.05 × 1.5) = 1.075
δ_actual = 1.0 + (0.10 × 1.5) = 1.150
```
**Result:** Stronger, more dramatic changes

### Strength = 2.0 (Maximum Effect)
```
λ_actual = 1.0 + (0.05 × 2.0) = 1.10
δ_actual = 1.0 + (0.10 × 2.0) = 1.20
```
**Result:** Very strong, dramatic changes

---

## Examples with "v2.2.1: Balanced" Preset

**Preset base values:** λ=1.0, δ=1.5 (more dramatic preset)

### Strength = 0.0 (No Effect)
```
λ_deviation = 1.0 - 1.0 = 0.0
δ_deviation = 1.5 - 1.0 = 0.5

λ_actual = 1.0 + (0.0 × 0.0) = 1.000
δ_actual = 1.0 + (0.5 × 0.0) = 1.000
```
**Result:** No change (neutral)

### Strength = 0.1 (Minimal Effect)
```
λ_actual = 1.0 + (0.0 × 0.1) = 1.000
δ_actual = 1.0 + (0.5 × 0.1) = 1.050
```
**Result:** Very subtle δ changes, λ stays neutral

### Strength = 0.5 (Half Effect)
```
λ_actual = 1.0 + (0.0 × 0.5) = 1.000
δ_actual = 1.0 + (0.5 × 0.5) = 1.250
```
**Result:** Moderate δ effect

### Strength = 1.0 (Preset's Intended Effect) ⭐
```
λ_actual = 1.0 + (0.0 × 1.0) = 1.000
δ_actual = 1.0 + (0.5 × 1.0) = 1.500
```
**Result:** Full preset effect (original values)

### Strength = 2.0 (Maximum Effect)
```
λ_actual = 1.0 + (0.0 × 2.0) = 1.000
δ_actual = 1.0 + (0.5 × 2.0) = 2.000
```
**Result:** Very strong δ effect (maximum slider range)

---

## Custom Mode (No Preset Selected)

When using "Custom" preset, the strength slider directly controls λ and δ:

```python
lambda_val = 1.0 + (0.2 × strength)
delta_val = 1.0 + (0.3 × strength)
```

### Examples:

| Strength | λ | δ | Effect |
|----------|---|---|--------|
| 0.0 | 1.000 | 1.000 | No change |
| 0.1 | 1.020 | 1.030 | Minimal |
| 0.5 | 1.100 | 1.150 | Gentle |
| 1.0 | 1.200 | 1.300 | Balanced |
| 1.5 | 1.300 | 1.450 | Strong |
| 2.0 | 1.400 | 1.600 | Very strong |

**Note:** Custom mode gives you visible effects at strength=1.0 without needing to understand preset values.

---

## Visual Guide

```
Strength Slider:  0.0 ←──────── 1.0 ────────→ 2.0
                   │             │             │
Effect Intensity:  None      Preset's      Double
                               Intended      Deviation
                               Effect        from Neutral

λ & δ Values:     1.0, 1.0    Preset     2×(Preset-1.0)+1.0
                  (neutral)    Values     (amplified)
```

---

## Recommended Strength Values

### For Testing/Exploration:
- **0.1 - 0.3**: Very subtle, good for A/B comparison
- **0.5**: Half-strength, gentle effects
- **1.0**: Preset's intended effect (recommended starting point)

### For Production:
- **0.8 - 1.2**: Safe range, balanced results
- **1.5 - 2.0**: Dramatic effects, use with caution

### For Debugging:
- **0.0**: Verify GRAG is working (should match original)
- **2.0**: Maximum effect, see full potential

---

## Console Output Example

When you use the Simple Controller, you'll see:

```
[GRAG Simple] Preset: Paper: Balanced
[GRAG Simple] Base parameters: λ=1.05, δ=1.10
[GRAG Simple] Strength slider: 0.50
[GRAG Simple] Scaled parameters: λ=1.025, δ=1.050
[GRAG Simple] Configuration embedded in conditioning
[GRAG Simple] Final strength: 0.50
```

This shows you:
1. Which preset you're using
2. The preset's original λ/δ values
3. Your strength slider setting
4. The **actual** λ/δ values being used (scaled)

---

## Why This Scaling Method?

### ✅ Advantages:
1. **Strength=0.0 always means NO change** (λ=1.0, δ=1.0)
2. **Strength=1.0 always uses preset's intended values**
3. **Linear scaling** is intuitive and predictable
4. **Works for any preset** (subtle or dramatic)
5. **No negative values** (all values ≥ 0)

### ❌ Old Method (Broken):
The old method just multiplied preset strength:
```python
final_strength = preset_strength × strength
```
This didn't actually change λ/δ values, making the slider ineffective!

---

## Comparison: Old vs New

### Using "Paper: Balanced" (λ=1.05, δ=1.10) at strength=0.1:

**Old Method (Broken):**
```
λ_actual = 1.05  (unchanged!)
δ_actual = 1.10  (unchanged!)
final_strength = 1.0 × 0.1 = 0.1  (only metadata changed)
```
**Problem:** λ/δ didn't change, so no visible difference!

**New Method (Fixed):**
```
λ_actual = 1.0 + (0.05 × 0.1) = 1.005  (closer to neutral)
δ_actual = 1.0 + (0.10 × 0.1) = 1.010  (closer to neutral)
final_strength = 0.1  (metadata matches reality)
```
**Result:** Actual minimal effect as expected!

---

## Technical Notes

### Parameter Ranges
The GRAG package supports λ and δ in range 0.1-2.0. The Simple Controller's strength slider maps:

```
Strength 0.0 → λ≥1.0, δ≥1.0 (neutral or higher)
Strength 2.0 → λ≤2.0, δ≤2.0 (within safe range)
```

### Preset Constraints
If a preset has λ<1.0 or δ<1.0 (reduction presets), the scaling works in reverse:

**Example:** Hypothetical preset with λ=0.9, δ=0.8
```
strength=0.0: λ=1.0, δ=1.0 (neutral)
strength=1.0: λ=0.9, δ=0.8 (reduction)
strength=2.0: λ=0.8, δ=0.6 (stronger reduction)
```

---

## FAQ

**Q: Why does strength=0.1 still show some effect?**
A: Because 0.1 means "10% of the preset's deviation from neutral". If the preset is λ=1.5, then:
- Deviation = 1.5 - 1.0 = 0.5
- At strength=0.1: λ = 1.0 + (0.5 × 0.1) = 1.05 (still different from 1.0)

**Q: What if I want absolutely zero effect?**
A: Use strength=0.0 or set enable_grag=False. Both give λ=1.0, δ=1.0 (neutral).

**Q: Can I get values below 1.0 with the Simple Controller?**
A: Only if your preset has λ<1.0 or δ<1.0. Most presets use values >1.0 for enhancement.

**Q: What's the difference between strength=1.0 and strength=2.0?**
A: strength=2.0 doubles the deviation from neutral. If preset is λ=1.1 (deviation=0.1):
- strength=1.0: λ=1.1 (preset value)
- strength=2.0: λ=1.2 (doubled deviation)

---

## Summary

The strength slider now works intuitively:

| Slider | Meaning | Visual Effect |
|--------|---------|--------------|
| 0.0 | Neutral (λ=1.0, δ=1.0) | No change |
| 0.1 | 10% of preset's effect | Minimal |
| 0.5 | 50% of preset's effect | Gentle |
| 1.0 | 100% (preset's intended) | Balanced ⭐ |
| 1.5 | 150% of preset's effect | Strong |
| 2.0 | 200% of preset's effect | Maximum |

**Start with strength=1.0 to see the preset's intended effect, then adjust up or down!**

---

**Author:** Amir Ferdos (ArchAi3d)
**Version:** 3.0.0
**License:** MIT
