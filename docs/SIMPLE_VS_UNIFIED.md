# GRAG Simple vs Unified Controller - Comparison Guide

## Quick Summary

| Feature | 🎛️ Simple Controller | 🎚️ Unified Controller |
|---------|---------------------|----------------------|
| **Target Users** | Beginners | Advanced users |
| **Parameters** | 3 (enable, preset, strength) | 25+ parameters |
| **Modes** | Preset-only | Simple / Advanced / Expert |
| **Presets** | Filtered (recommended only) | All 54 presets |
| **Per-layer Control** | ❌ No | ✅ Yes (Advanced mode) |
| **Adaptive Timestep** | ❌ No | ✅ Yes (Expert mode) |
| **Multi-Resolution** | ❌ No | ✅ Yes (Expert mode) |
| **Learning Curve** | 5 minutes | 30-60 minutes |
| **Best For** | Quick results, testing | Precision control, research |

---

## 🎛️ GRAG Simple Controller

### When to Use
- ✅ You're new to GRAG
- ✅ You want quick results without learning complex parameters
- ✅ You're testing different presets to find what works
- ✅ You only need basic control (on/off + intensity)
- ✅ You prefer simplicity over fine-tuning

### Parameters (Only 3!)

1. **enable_grag** (Boolean)
   - Turn GRAG effects on/off
   - Default: True
   - Simple toggle switch

2. **preset** (Dropdown - Recommended presets only)
   - Choose from curated beginner-friendly presets:
     - **Paper: Balanced** ⭐ (Recommended - λ=1.05, δ=1.10)
     - **Paper: Subtle** (Gentle effects - λ=1.02, δ=1.03)
     - **v2.2.1: Balanced** (Proven preset - λ=1.0, δ=1.5)
     - **Clean Room: Gentle** (For interior design)
     - **Custom** (Auto-calculated from strength)

3. **strength** (Slider: 0.0 - 2.0)
   - Overall effect intensity
   - 0.0 = No effect (disabled)
   - 1.0 = Preset's original strength
   - 2.0 = Double the preset's strength
   - Step: 0.1 (easy adjustment)

### Example Workflow
```
[Load Image]
    ↓
[Qwen Encoder V2]
    ↓
[🎛️ GRAG Simple Controller]
├─ enable_grag: True
├─ preset: "Paper: Balanced"  ← Recommended!
└─ strength: 1.0
    ↓
[⚙️ GRAG Advanced Sampler]
├─ steps: 20
├─ cfg: 8.0
└─ sampler: euler
    ↓
[VAE Decode] → [Save Image]
```

### Console Output Example
```
[GRAG Simple] Preset: Paper: Balanced
[GRAG Simple] Base parameters: λ=1.05, δ=1.10
[GRAG Simple] Strength multiplier: 1.0x
[GRAG Simple] Configuration embedded in conditioning
[GRAG Simple] Final strength: 1.00
```

### Pros & Cons

**Pros:**
- ✅ Super easy to use - 3 parameters only
- ✅ No need to understand λ (lambda) and δ (delta)
- ✅ Curated presets - only recommended options shown
- ✅ Strength slider - intuitive intensity control
- ✅ Perfect for beginners and quick testing

**Cons:**
- ❌ No per-layer control
- ❌ No adaptive timestep scheduling
- ❌ No multi-resolution tiers
- ❌ Limited preset selection (filtered)
- ❌ Less precision for advanced editing

---

## 🎚️ GRAG Unified Controller

### When to Use
- ✅ You understand λ (lambda) and δ (delta) parameters
- ✅ You need per-layer control for precision editing
- ✅ You want adaptive timestep scheduling
- ✅ You're using multi-resolution workflows
- ✅ You want full access to all 54 presets
- ✅ You need maximum control and flexibility

### Parameters (25+ parameters organized by mode)

#### **Simple Mode** (Like Simple Controller, but with more presets)
- enable_grag
- preset (all 54 presets available)
- lambda_global
- delta_global
- strength_multiplier

#### **Advanced Mode** (Per-layer control)
All Simple Mode parameters +
- per_layer_enabled
- layer_strategy (structure_preserving, semantic_focused, etc.)
- lambda_start / lambda_end
- delta_start / delta_end
- total_layers

#### **Expert Mode** (Full control)
All Advanced Mode parameters +
- **Adaptive Timestep:**
  - adaptive_enabled
  - adaptive_schedule
  - multiplier_start / multiplier_end
- **Multi-Resolution:**
  - multi_resolution_enabled
  - tier_preset
  - tier1_resolution, tier1_lambda, tier1_delta
  - tier2_resolution, tier2_lambda, tier2_delta

### Example Workflow (Simple Mode)
```
[Load Image]
    ↓
[Qwen Encoder V2]
    ↓
[🎚️ GRAG Unified Controller]
├─ enable_grag: True
├─ control_mode: "simple"
├─ preset: "Paper: Balanced"
├─ lambda_global: 1.05
├─ delta_global: 1.10
└─ strength_multiplier: 1.0
    ↓
[⚙️ GRAG Advanced Sampler] → [Output]
```

### Example Workflow (Advanced Mode - Per-Layer)
```
[Load Image]
    ↓
[Qwen Encoder V2]
    ↓
[🎚️ GRAG Unified Controller]
├─ enable_grag: True
├─ control_mode: "advanced"
├─ per_layer_enabled: True
├─ layer_strategy: "structure_preserving"
├─ lambda_start: 0.9  (early layers - less effect)
├─ lambda_end: 1.3    (late layers - more effect)
├─ delta_start: 0.9
├─ delta_end: 1.3
└─ total_layers: 60
    ↓
[⚙️ GRAG Advanced Sampler] → [Output]
```

### Console Output Example (Advanced Mode)
```
[GRAG v3.0] Advanced Mode - Custom parameters
[GRAG v3.0] Global: λ=1.05, δ=1.10
[GRAG v3.0] Per-layer control enabled: structure_preserving strategy
[GRAG v3.0] λ range: 0.90-1.30
[GRAG v3.0] δ range: 0.90-1.30
[GRAG v3.0] Configuration embedded in conditioning
```

### Pros & Cons

**Pros:**
- ✅ Full control over all GRAG features
- ✅ Per-layer control for precision editing
- ✅ Adaptive timestep scheduling
- ✅ Multi-resolution tier support
- ✅ All 54 presets available
- ✅ Progressive complexity (Simple → Advanced → Expert)
- ✅ Research-grade capabilities

**Cons:**
- ❌ Steep learning curve (need to understand GRAG concepts)
- ❌ Many parameters can be overwhelming
- ❌ Easy to misconfigure if inexperienced
- ❌ Requires understanding of λ/δ mathematics
- ❌ More time needed for experimentation

---

## Which Should You Use?

### Start with 🎛️ Simple Controller if:
1. You're new to GRAG
2. You don't know what λ (lambda) and δ (delta) mean
3. You want results in 5 minutes or less
4. You're just exploring what GRAG can do
5. You prefer preset-based workflows

### Upgrade to 🎚️ Unified Controller when:
1. You understand GRAG concepts (λ, δ, bias, deviation)
2. You need per-layer control for specific editing tasks
3. You want to create custom presets
4. You need adaptive timestep scheduling
5. You're working on research or advanced projects
6. You've mastered Simple Controller and want more

---

## Migration Path

### Phase 1: Learn with Simple Controller
```
🎛️ Simple Controller (Week 1-2)
├─ Try "Paper: Balanced" preset
├─ Experiment with strength slider (0.5 - 2.0)
├─ Test different presets
└─ Learn what effects you like
```

### Phase 2: Understand Unified Controller (Simple Mode)
```
🎚️ Unified Controller - Simple Mode (Week 3-4)
├─ Set control_mode: "simple"
├─ Manually adjust lambda_global and delta_global
├─ Understand how λ affects bias strength
├─ Understand how δ affects deviation intensity
└─ Create your first custom preset
```

### Phase 3: Advanced Features
```
🎚️ Unified Controller - Advanced Mode (Week 5-6)
├─ Enable per_layer_enabled
├─ Try "structure_preserving" strategy
├─ Experiment with lambda_start/end ranges
└─ Compare results with Simple mode
```

### Phase 4: Expert Control
```
🎚️ Unified Controller - Expert Mode (Week 7+)
├─ Enable adaptive_enabled
├─ Try "diffusion_aligned" schedule
├─ Enable multi_resolution_enabled
├─ Combine all features for maximum control
└─ Publish your custom presets!
```

---

## Technical Differences

### Parameter Count
- **Simple Controller:** 3 user-facing parameters
- **Unified Controller:** 25+ parameters (organized by mode)

### Preset Filtering
- **Simple Controller:** Shows only recommended presets (~10 presets)
  - Custom
  - All "Paper:" presets
  - v2.2.1: Balanced
  - All "Clean Room:" presets
- **Unified Controller:** Shows all 54 presets
  - All of the above +
  - 41 v2.2.1 experimental presets (Preset 01-41)
  - Conservative presets
  - All categories visible

### Strength Handling
- **Simple Controller:**
  - Single strength slider (0.0-2.0, step 0.1)
  - Multiplies preset values
  - Custom mode auto-calculates λ/δ from strength
- **Unified Controller:**
  - Strength multiplier (0.0-2.0, step 0.01)
  - Manual λ and δ control
  - Per-layer λ/δ ranges
  - Adaptive timestep multipliers

### Output Metadata
Both controllers output identical conditioning metadata format:
```python
metadata = {
    'grag_enabled': True,
    'grag_lambda': 1.05,  # or list for per-layer
    'grag_delta': 1.10,   # or list for per-layer
    'grag_strength_multiplier': 1.0,
    'grag_control_mode': 'simple',  # or 'advanced', 'expert'
    # ... additional metadata for advanced features
}
```

Both work with the same **GRAG Advanced Sampler**.

---

## Recommended Workflows

### Beginner Workflow (Quick Results)
```
[Image] → [Encoder] → [🎛️ Simple Controller] → [GRAG Sampler] → [Output]
                      └─ preset: "Paper: Balanced"
                      └─ strength: 1.0
```

### Intermediate Workflow (Custom Parameters)
```
[Image] → [Encoder] → [🎚️ Unified Controller] → [GRAG Sampler] → [Output]
                      ├─ mode: "simple"
                      ├─ lambda: 1.1
                      └─ delta: 1.2
```

### Advanced Workflow (Per-Layer Control)
```
[Image] → [Encoder] → [🎚️ Unified Controller] → [GRAG Sampler] → [Output]
                      ├─ mode: "advanced"
                      ├─ per_layer: True
                      ├─ strategy: "structure_preserving"
                      └─ λ: 0.9→1.3, δ: 0.9→1.3
```

### Expert Workflow (Full Control)
```
[Image] → [Encoder] → [🎚️ Unified Controller] → [GRAG Sampler] → [Output]
                      ├─ mode: "expert"
                      ├─ per_layer: True
                      ├─ adaptive: True (diffusion_aligned)
                      └─ multi_res: True (tier1: 512px, tier2: 4096px)
```

---

## FAQ

**Q: Can I use both controllers in the same workflow?**
A: No - only connect one controller to the GRAG Advanced Sampler. The last controller in the chain will override previous ones.

**Q: Will Simple Controller results be identical to Unified Controller (simple mode)?**
A: Almost identical when using the same preset and strength=1.0. Simple Controller uses step=0.1 for strength, Unified uses step=0.01 for more precision.

**Q: Can I save presets from Simple Controller?**
A: No - use the Preset Manager node or manually edit YAML files. Simple Controller is read-only for simplicity.

**Q: Does Simple Controller support all 54 presets?**
A: No - it filters to show only recommended presets (~10 presets). Use Unified Controller for all 54 presets.

**Q: Which is faster?**
A: Identical runtime performance. UI complexity is the only difference.

---

## Conclusion

**Choose Simple Controller** for:
- Beginner-friendly experience
- Quick experimentation
- Preset-based workflows
- Learning GRAG basics

**Choose Unified Controller** for:
- Advanced features (per-layer, adaptive, multi-res)
- Custom parameter control
- Research and precision editing
- Maximum flexibility

**Both controllers are compatible with the same GRAG Advanced Sampler!**

---

**Author:** Amir Ferdos (ArchAi3d)
**Version:** 3.0.0
**License:** MIT
