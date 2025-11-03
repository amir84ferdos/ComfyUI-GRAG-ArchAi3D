# GRAG v3.0 - Quick Start Guide

Get started with GRAG (Group-Relative Attention Guidance) v3.0 in 5 minutes!

---

## 📖 Table of Contents

1. [What You Need](#what-you-need)
2. [Simple Mode (Beginner)](#simple-mode-beginner)
3. [Advanced Mode (Per-Layer)](#advanced-mode-per-layer)
4. [Expert Mode (Adaptive + Multi-Res)](#expert-mode-expert)
5. [Preset Management](#preset-management)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 What You Need

**Required Nodes:**
- Any image encoder (Qwen Encoder, Flux Encoder, SD3 Encoder, etc.)
- **GRAG Unified Controller v3.0** (🎚️)
- **GRAG Advanced Sampler v3.0** (⚙️)
- VAE Decoder
- Image output

**Recommended Setup:**
```
[Image] → [Qwen Encoder V2] → [GRAG Unified Controller] → [GRAG Advanced Sampler] → [VAE Decode] → [Save]
```

---

## 🟢 Simple Mode (Beginner)

**Best for:** First-time GRAG users, quick testing

### Step 1: Basic Workflow

```
[Load Image] → [Qwen Encoder V2]
                ↓
            [GRAG Unified Controller v3.0]
            ├─ enable_grag: True
            ├─ control_mode: "simple"
            ├─ preset: "Paper: Balanced"  ⭐ START HERE
            └─ Output: CONDITIONING
                ↓
            [GRAG Advanced Sampler v3.0]
            ├─ steps: 20
            ├─ cfg: 8.0
            ├─ sampler: euler
            └─ Output: LATENT
                ↓
            [VAE Decode] → [Save Image]
```

### Step 2: Choose a Preset

**Recommended presets for beginners:**

| Preset | Parameters | Use Case |
|--------|------------|----------|
| **Paper: Balanced** ⭐ | λ=1.05, δ=1.10 | **Start here!** General editing |
| **Paper: Subtle** | λ=1.00, δ=1.05 | Gentle transformations |
| **v2.2.1: Balanced** | λ=1.00, δ=1.50 | Visible effects (v2.2.1 proven) |
| **Clean Room: Gentle** | λ=0.85, δ=1.15 | Preserve windows, remove scaffolding |

### Step 3: Test and Adjust

1. **Generate with "Paper: Balanced"**
   - If too subtle → Try "v2.2.1: Balanced" or "Paper: Moderate"
   - If too strong → Try "Paper: Subtle" or "Preset 12" (v2.2.1)

2. **For Clean Room workflow:**
   - Start with "Clean Room: Gentle"
   - If scaffolding remains → "Clean Room: Balanced"
   - If windows change too much → Lower preset (Preset 07-10)

3. **Console output shows:**
   ```
   [GRAG v3.0] Simple Mode - Preset: Paper: Balanced
   [GRAG v3.0] Parameters: λ=1.05, δ=1.10, strength=1.00
   [GRAG v3.0] Patched 60 Attention layers
   ```

---

## 🟡 Advanced Mode (Per-Layer)

**Best for:** Precision control, structure preservation

### When to Use Per-Layer Control

- You want gentle edits in early layers (preserve structure)
- You want strong edits in late layers (enhance details)
- Clean Room workflow with window preservation

### Step 1: Enable Per-Layer

```
[GRAG Unified Controller v3.0]
├─ enable_grag: True
├─ control_mode: "advanced"  ← Change to advanced
├─ per_layer_enabled: True   ← Enable per-layer
├─ layer_strategy: "structure_preserving"  ⭐ START HERE
├─ total_layers: 60  (Qwen default)
└─ Output: CONDITIONING
```

### Step 2: Choose Strategy

| Strategy | Lambda Range | Delta Range | Use Case |
|----------|--------------|-------------|----------|
| **structure_preserving** ⭐ | 0.9 → 1.2 | 0.9 → 1.3 | **Recommended:** Preserve structure, enhance details |
| **semantic_focused** | 0.9 → 0.9 (bell) | 1.0 → 1.0 (bell) | Style transfer, object replacement |
| **detail_enhancer** | 1.3 → 1.3 (U) | 1.3 → 1.3 (U) | Material changes, texture enhancement |
| **balanced_progressive** | 1.0 → 1.3 | 1.0 → 1.3 | General use, testing |

### Step 3: Custom Per-Layer (Optional)

```
[GRAG Unified Controller v3.0]
├─ layer_strategy: "custom"
├─ lambda_start: 0.85  ← Early layers (preserve)
├─ lambda_end: 1.40    ← Late layers (transform)
├─ delta_start: 0.90
├─ delta_end: 1.50
```

**Effect:**
- Layers 0-20: Gentle (λ=0.85-1.0, preserve structure)
- Layers 20-40: Moderate (λ=1.0-1.2, balanced)
- Layers 40-60: Strong (λ=1.2-1.4, enhance details)

---

## 🔴 Expert Mode (Adaptive + Multi-Resolution)

**Best for:** Maximum control, research, experimentation

### Adaptive Timestep Scheduling

**What it does:** Varies GRAG intensity during denoising

```
[GRAG Unified Controller v3.0]
├─ control_mode: "expert"
├─ adaptive_enabled: True
├─ adaptive_schedule: "smooth_transition"  ⭐ START HERE
├─ multiplier_start: 0.8   ← Early steps (gentle)
├─ multiplier_end: 1.5     ← Late steps (strong)
```

**Schedule Types:**

| Schedule | Behavior | Use Case |
|----------|----------|----------|
| **smooth_transition** ⭐ | Sine S-curve (0.85→1.4) | **Recommended:** Natural edits |
| **gentle_to_strong** | Linear (0.8→1.5) | Predictable progression |
| **conservative** | Exponential (0.9→1.2) | Preserve structure |
| **aggressive** | Exponential (0.8→1.8) | Dramatic transformation |
| **diffusion_aligned** | Cosine (0.8→1.5) | Matches model's noise schedule |

### Multi-Resolution Tiers

**What it does:** Different GRAG parameters for different resolutions (Paper's method)

```
[GRAG Unified Controller v3.0]
├─ multi_resolution_enabled: True
├─ tier_preset: "v221_visible"  ⭐ START HERE
│
├─ Tier 1 (Structure):
│   ├─ tier1_resolution: 512
│   ├─ tier1_lambda: 0.9   (gentle on coarse features)
│   └─ tier1_delta: 0.9
│
└─ Tier 2 (Details):
    ├─ tier2_resolution: 4096
    ├─ tier2_lambda: 1.3   (strong on fine details)
    └─ tier2_delta: 1.3
```

**Tier Presets:**

| Preset | Tier 1 (512px) | Tier 2 (4096px) | Use Case |
|--------|----------------|-----------------|----------|
| **v221_visible** ⭐ | λ=0.9, δ=0.9 | λ=1.3, δ=1.3 | Visible effects, balanced |
| **paper_stable** | λ=1.0, δ=1.0 | λ=1.05, δ=1.10 | Paper-validated, stable |
| **structure_preserving** | λ=1.0, δ=1.0 | λ=0.85, δ=1.15 | Preserve structure, gentle details |
| **detail_focused** | λ=1.0, δ=1.0 | λ=1.5, δ=1.8 | Neutral structure, strong details |

---

## 💾 Preset Management

### Save Your Custom Preset

```
[GRAG Preset Manager v3.0]
├─ mode: "save"
├─ preset_name: "my_clean_room_preset"
├─ lambda_value: 0.90
├─ delta_value: 1.25
├─ strength_value: 1.0
├─ description: "Perfect for my clean room workflow"
├─ category: "user_custom"
└─ use_case: "architectural edits"
```

**Output:** Saved to `presets/user_custom.yaml`

### Load a Preset

```
[GRAG Preset Manager v3.0]
├─ mode: "load"
└─ preset_name: "my_clean_room_preset"
    └─ Returns: (lambda, delta, strength, info)
```

**Connect outputs:**
- lambda → GRAG Unified Controller's `lambda_global`
- delta → GRAG Unified Controller's `delta_global`
- strength → GRAG Unified Controller's `strength_multiplier`

### Show Preset Info

```
[GRAG Preset Manager v3.0]
├─ mode: "info"
└─ preset_name: "Paper: Balanced"
```

**Output (in info string):**
```
📊 Preset Information: 'Paper: Balanced'
==================================================
Parameters:
  λ (lambda): 1.05
  δ (delta):  1.10
  Strength:   1.00

Metadata:
  Category:    paper_stable
  Use Case:    general editing, first-time GRAG use
  Description: Recommended starting point (paper validated)
```

---

## 🔧 Troubleshooting

### Problem: No visible effect

**Causes:**
1. GRAG not enabled
2. Parameters at neutral (λ=1.0, δ=1.0 produces NO change)
3. Not using GRAG Advanced Sampler

**Solutions:**
- ✅ Set `enable_grag: True` in Unified Controller
- ✅ Use preset with λ≠1.0 or δ≠1.0 (try "Paper: Balanced")
- ✅ Connect to **GRAG Advanced Sampler**, not standard KSampler

### Problem: Console shows "GRAG disabled"

**Check:**
```
[GRAG Unified Controller v3.0]
└─ enable_grag: True  ← Must be enabled!
```

### Problem: Console shows "0 Attention layers patched"

**Causes:**
- Model not supported (not Qwen architecture)
- Model loading failed

**Solutions:**
- Verify you're using Qwen-based model
- Check console for earlier errors
- Try restarting ComfyUI

### Problem: Too subtle even with high values

**Try:**
1. Use v2.2.1 proven presets (wider range)
   - "v2.2.1: Balanced" (λ=1.0, δ=1.5)
   - "v2.2.1: Strong" (λ=1.3, δ=1.5)
   - "v2.2.1: Maximum" (λ=1.5, δ=2.0)

2. Switch to Custom mode:
   ```
   preset: "Custom"
   lambda_global: 1.50
   delta_global: 2.00
   ```

### Problem: Too strong, artifacts appear

**Solutions:**
1. Lower parameters:
   - Try "Paper: Subtle" (λ=1.0, δ=1.05)
   - Or "Preset 12" (λ=0.58, δ=0.60) from v2.2.1

2. Use per-layer with gentle start:
   ```
   per_layer_enabled: True
   lambda_start: 0.85
   lambda_end: 1.15
   ```

### Problem: Windows changing in Clean Room

**Solutions:**
1. Use Clean Room presets:
   - "Clean Room: Gentle" (λ=0.85, δ=1.15)

2. Enable per-layer with structure preservation:
   ```
   per_layer_enabled: True
   layer_strategy: "structure_preserving"
   ```

3. Lower delta more than lambda:
   ```
   lambda_global: 0.95
   delta_global: 1.10
   ```

---

## 📊 Parameter Guidelines

### Understanding λ (Lambda) and δ (Delta)

**λ (Lambda) - Bias Strength:**
- `< 1.0`: Reduces shared patterns (more variety)
- `= 1.0`: Neutral (no change to bias)
- `> 1.0`: Enhances shared patterns (more consistency)

**δ (Delta) - Deviation Intensity:**
- `< 1.0`: Suppresses differences (smoother, uniform)
- `= 1.0`: Neutral (no change to deviation)
- `> 1.0`: Amplifies differences (more variation, details)

### **CRITICAL:** Why λ=1.0, δ=1.0 produces NO change

```
Mathematical formula:
k̂ = λ * k_mean + δ * (k - k_mean)

At λ=1.0, δ=1.0:
k̂ = 1.0 * k_mean + 1.0 * (k - k_mean)
  = k_mean + k - k_mean
  = k  (UNCHANGED!)
```

**Always use λ≠1.0 or δ≠1.0 for visible effects!**

### Recommended Ranges

| Effect | Lambda (λ) | Delta (δ) |
|--------|------------|-----------|
| Gentle | 0.90-1.05 | 1.00-1.15 |
| Balanced | 1.00-1.15 | 1.10-1.30 |
| Strong | 1.15-1.50 | 1.30-1.80 |
| Maximum | 1.50-2.00 | 1.80-2.00 |

---

## 🎯 Example Workflows

### Example 1: Simple Clean Room

```
[Load Room Image]
    ↓
[Clean Room Prompt] → "remove scaffolding, clean walls"
    ↓
[Qwen Encoder V2]
    ↓
[GRAG Unified Controller]
├─ enable_grag: True
├─ preset: "Clean Room: Gentle"
    ↓
[GRAG Advanced Sampler]
├─ steps: 20, cfg: 8.0
    ↓
[VAE Decode] → [Save]
```

### Example 2: Material Change with Per-Layer

```
[Load Interior Image]
    ↓
[Text Prompt] → "change floor to marble"
    ↓
[Qwen Encoder V2]
    ↓
[GRAG Unified Controller]
├─ enable_grag: True
├─ control_mode: "advanced"
├─ per_layer_enabled: True
├─ layer_strategy: "detail_enhancer"
    ↓
[GRAG Advanced Sampler]
    ↓
[VAE Decode] → [Save]
```

### Example 3: Maximum Control (All Features)

```
[Load Image]
    ↓
[Complex Prompt]
    ↓
[Qwen Encoder V2]
    ↓
[GRAG Unified Controller]
├─ control_mode: "expert"
├─ per_layer_enabled: True
├─ adaptive_enabled: True
├─ multi_resolution_enabled: True
├─ layer_strategy: "structure_preserving"
├─ adaptive_schedule: "smooth_transition"
├─ tier_preset: "v221_visible"
    ↓
[GRAG Advanced Sampler]
├─ debug_mode: True  ← Enable detailed logging
    ↓
[VAE Decode] → [Save]
```

---

## 📚 Next Steps

- **[Parameter Guide](PARAMETER_GUIDE.md)** - Deep dive into λ, δ, and how they work
- **[Migration Guide](MIGRATION_GUIDE.md)** - Upgrade from v2.2.1 to v3.0
- **[Advanced Usage](ADVANCED_USAGE.md)** - Expert techniques and optimization

---

## 💬 Support

**Questions? Issues?**
- GitHub: https://github.com/amir84ferdos/ComfyUI-ArchAi3d-Qwen
- Email: Amir84ferdos@gmail.com
- LinkedIn: https://www.linkedin.com/in/archai3d/

---

**Version:** 3.0.0
**Last Updated:** 2025-11-03
**Author:** Amir Ferdos (ArchAi3d)
**License:** MIT (Free for all uses)

Happy GRAG-ing! 🎨✨
