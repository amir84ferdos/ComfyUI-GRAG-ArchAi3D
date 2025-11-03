# GRAG v3.0 - Advanced Group-Relative Attention Guidance

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-orange.svg)](https://github.com/comfyanonymous/ComfyUI)

**Professional-grade GRAG implementation for ComfyUI with advanced features and beginner-friendly interface.**

## 🎯 What is GRAG?

GRAG (Group-Relative Attention Guidance) is a training-free image editing technique that provides fine-grained control over diffusion models by reweighting attention keys. This implementation is based on the research paper [arXiv 2510.24657](https://arxiv.org/abs/2510.24657).

### Key Formula

```
k̂ = λ × k_mean + δ × (k - k_mean)
```

Where:
- **λ (lambda)**: Controls bias strength (>1 enhances, <1 reduces)
- **δ (delta)**: Controls deviation intensity (>1 amplifies, <1 suppresses)
- **k_mean**: Group bias (mean of attention keys)
- **(k - k_mean)**: Token deviation from group

## ✨ Features

### 🎛️ Two Controller Options
- **Simple Controller**: Beginner-friendly with 3 parameters (preset, strength, optional λ/δ overrides)
- **Unified Controller**: Advanced control with 25+ parameters (per-layer, adaptive, multi-resolution)

### 🎨 Core Capabilities
- ✅ **54 Presets** (41 v2.2.1 tested + 13 paper-recommended)
- ✅ **Per-Layer Control** - Different λ/δ per transformer block
- ✅ **Adaptive Timestep** - Vary strength during denoising
- ✅ **Multi-Resolution** - Paper's 2-tier system (512px, 4096px)
- ✅ **Architecture Auto-Detection** - Works with Qwen, Flux, SD3, etc.
- ✅ **Preset Management** - Save/load/share custom configurations

### 🛡️ Quality Assurance
- ✅ **v2.2.1 Contamination Fix** - try/finally restoration prevents global state pollution
- ✅ **PyYAML Optional** - Works with 5 hardcoded presets, full library with PyYAML
- ✅ **Debug Mode** - Attention analysis and performance metrics
- ✅ **Extensive Documentation** - Guides for all skill levels

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "GRAG" or "ArchAi3d"
3. Click Install
4. Restart ComfyUI

### Method 2: Git Clone
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/amir84ferdos/ComfyUI-GRAG.git GRAG
cd GRAG
pip install -r requirements.txt  # Optional: For full 54-preset library
```

### Method 3: Manual Download
1. Download ZIP from [GitHub Releases](https://github.com/amir84ferdos/ComfyUI-GRAG/releases)
2. Extract to `ComfyUI/custom_nodes/GRAG/`
3. (Optional) Install PyYAML: `pip install PyYAML`
4. Restart ComfyUI

### Dependencies
- **Required**: ComfyUI, PyTorch
- **Optional**: PyYAML (for full 54-preset library)
  - Without PyYAML: 5 essential presets
  - With PyYAML: All 54 presets

## 🚀 Quick Start

### Beginner Workflow (Simple Controller)
```
[Load Image]
    ↓
[Qwen Encoder V2]
    ↓
[🎛️ GRAG Simple Controller]
├─ enable_grag: True
├─ preset: "Paper: Balanced"  ⭐ Recommended
├─ strength: 1.0              (0.0-2.0)
└─ lambda/delta_override: -1.0 (optional)
    ↓
[⚙️ GRAG Advanced Sampler]
├─ steps: 20
├─ cfg: 8.0
└─ sampler: euler
    ↓
[VAE Decode] → [Save Image]
```

### Advanced Workflow (Unified Controller)
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
└─ lambda/delta ranges: 0.9-1.3
    ↓
[⚙️ GRAG Advanced Sampler] → [Output]
```

## 📊 Available Nodes

### 1. 🎛️ GRAG Simple Controller v3.0
**Beginner-friendly preset-based control**

**Parameters:**
- `enable_grag` (Boolean): On/off toggle
- `preset` (Dropdown): Curated presets (Custom, Paper: Balanced, etc.)
- `strength` (Float 0-2): Effect intensity
  - 0.0 = No change
  - 1.0 = Preset's intended effect
  - 2.0 = Very strong
- `lambda_override` (Optional Float): Manual λ control (-1.0=auto, 0.1-2.0=custom)
- `delta_override` (Optional Float): Manual δ control (-1.0=auto, 0.1-2.0=custom)

**Best For:**
- Beginners new to GRAG
- Quick experimentation
- Preset-based workflows

### 2. 🎚️ GRAG Unified Controller v3.0
**Advanced multi-mode control**

**Modes:**
- **Simple**: Preset + manual λ/δ (like Simple Controller but all 54 presets)
- **Advanced**: Per-layer control (different λ/δ per transformer block)
- **Expert**: Adaptive timestep + Multi-resolution

**Best For:**
- Advanced users
- Precision editing
- Research and custom workflows

### 3. ⚙️ GRAG Advanced Sampler v3.0
**Enhanced sampler with GRAG patches**

**Features:**
- Monkey-patches Qwen attention layers
- v2.2.1 contamination fix (try/finally restoration)
- Compatible with both controllers
- Debug mode for attention analysis

### 4. 💾 GRAG Preset Manager v3.0
**Save/load/manage custom presets**

**Operations:**
- Save current parameters as named preset
- Load user-saved presets
- Delete user presets
- Export/share preset configurations

## 📚 Documentation

### Essential Guides
- **[INSTALL.md](INSTALL.md)** - Installation and troubleshooting
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Getting started guide
- **[docs/SIMPLE_VS_UNIFIED.md](docs/SIMPLE_VS_UNIFIED.md)** - Controller comparison
- **[docs/STRENGTH_SLIDER_EXPLAINED.md](docs/STRENGTH_SLIDER_EXPLAINED.md)** - Strength slider mechanics

### Technical Documentation
- **[SIMPLE_CONTROLLER_UPDATES.md](SIMPLE_CONTROLLER_UPDATES.md)** - Recent improvements
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - Import fixes and troubleshooting
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Full implementation details

## 🎨 Preset Library

### Categories
1. **Paper-Recommended** (5 presets)
   - Paper: Subtle (λ=1.02, δ=1.03)
   - **Paper: Balanced** (λ=1.05, δ=1.10) ⭐ Recommended
   - Paper: Moderate (λ=1.08, δ=1.15)
   - Paper: Strong (λ=1.10, δ=1.20)
   - Paper: Maximum (λ=1.15, δ=1.25)

2. **v2.2.1 Tested** (3 presets)
   - v2.2.1: Balanced (λ=1.0, δ=1.5)
   - v2.2.1: Conservative (λ=1.0, δ=1.3)
   - v2.2.1: Dramatic (λ=1.2, δ=1.8)

3. **Clean Room Workflow** (3 presets)
   - Clean Room: Gentle (λ=1.03, δ=1.05)
   - Clean Room: Balanced (λ=1.05, δ=1.10)
   - Clean Room: Strong (λ=1.08, δ=1.15)

4. **v2.2.1 Experimental** (41 presets)
   - Preset 01-41 (range: 0.56-0.64)
   - Structure-preserving, tested in production

5. **Conservative Extended** (2 presets)
   - Conservative: Low (λ=1.02, δ=1.05)
   - Conservative: High (λ=1.08, δ=1.12)

**Total: 54 presets** (5 without PyYAML, 54 with PyYAML)

## 📈 Parameter Ranges

| Parameter | Range | Default | Recommended |
|-----------|-------|---------|-------------|
| λ (lambda) | 0.1-2.0 | 1.0 | 0.8-1.5 |
| δ (delta) | 0.1-2.0 | 1.05 | 0.8-1.5 |
| Strength | 0.0-2.0 | 1.0 | 0.8-1.5 |

**Critical:** At λ=1.0, δ=1.0, the formula produces **NO change** (neutral point).

## 🔬 Mathematical Foundation

### GRAG Formula
```python
# Decompose attention key into bias and deviation
k_bias = mean(k_1, k_2, ..., k_N)  # Group bias
Δk_i = k_i - k_bias                 # Token deviation

# Reweight with λ and δ
k̂_i = λ × k_bias + δ × Δk_i
```

### Strength Scaling (Simple Controller)
```python
# Scale from neutral (1.0) based on strength
lambda_deviation = lambda_preset - 1.0
delta_deviation = delta_preset - 1.0

lambda_actual = 1.0 + (lambda_deviation × strength)
delta_actual = 1.0 + (delta_deviation × strength)
```

## 🛠️ Advanced Features

### Per-Layer Control
Different λ/δ values per transformer block for precision editing.

**Strategies:**
- Linear: Smooth progression from start to end
- U-shaped: Lower in middle layers, higher at extremes
- Bell-curve: Higher in middle layers, lower at extremes
- Custom: Manual layer-specific values

### Adaptive Timestep Scheduling
Vary GRAG strength during denoising process.

**Schedules:**
- Linear: Constant progression
- Exponential: Gradual then rapid change
- Sine/Cosine: Smooth transitions
- Diffusion-aligned: Matches noise schedule

### Multi-Resolution Tiers
Paper's 2-tier system for hierarchical control.

**Configuration:**
- Tier 1 (512px): Coarse structure (typically λ=1.0, δ=1.0)
- Tier 2 (4096px): Fine details (custom λ/δ)

## 🐛 Troubleshooting

### Nodes Not Appearing
1. **Restart ComfyUI** (required after installation)
2. Check console for error messages
3. Verify package location: `ComfyUI/custom_nodes/GRAG/`
4. Check `__init__.py` exists

### Only 5 Presets Available
**Cause:** PyYAML not installed

**Solution:**
```bash
pip install PyYAML
# Restart ComfyUI
```

### No Visible GRAG Effects
1. ✅ Using **GRAG Advanced Sampler** (not standard KSampler)
2. ✅ `enable_grag: True` in controller
3. ✅ Preset with λ≠1.0 or δ≠1.0
4. ✅ Console shows "Patched XX Attention layers"

### Import Errors
See [FIXES_APPLIED.md](FIXES_APPLIED.md) for detailed troubleshooting.

## 📞 Support

### Getting Help
- **Issues:** [GitHub Issues](https://github.com/amir84ferdos/ComfyUI-GRAG/issues)
- **Email:** Amir84ferdos@gmail.com
- **LinkedIn:** [ArchAi3d](https://www.linkedin.com/in/archai3d/)

### Contributing
Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## 📜 License

MIT License - Free for all uses (personal and commercial)

```
Copyright (c) 2025 Amir Ferdos (ArchAi3d)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## 🙏 Credits

**Based on:**
- [arXiv 2510.24657](https://arxiv.org/abs/2510.24657) - GRAG-Image-Editing paper
- [little-misfit's GRAG repository](https://github.com/little-misfit/GRAG-Image-Editing)
- v2.2.1 implementation learnings (ArchAi3d-Qwen package)

**Author:** Amir Ferdos (ArchAi3d)
**Email:** Amir84ferdos@gmail.com
**LinkedIn:** https://www.linkedin.com/in/archai3d/
**GitHub:** https://github.com/amir84ferdos

## 🗺️ Roadmap

- [x] Core algorithms (attention_v3, per-layer, adaptive, multi-res)
- [x] 54-preset library (v2.2.1 + paper + proven)
- [x] Simple Controller (beginner-friendly)
- [x] Unified Controller (advanced/expert modes)
- [x] Advanced Sampler (v2.2.1 contamination fix)
- [x] Preset Manager (save/load/share)
- [x] Comprehensive documentation
- [ ] Attention visualizer (future)
- [ ] Example workflows repository
- [ ] Video tutorials

## 📊 Version History

### v3.0.0 (2025-11-03)
- ✅ Complete rewrite with modular architecture
- ✅ Simple Controller for beginners
- ✅ Unified Controller with 3 modes
- ✅ 54 presets (41 v2.2.1 + 13 new)
- ✅ Per-layer, adaptive, multi-resolution support
- ✅ v2.2.1 contamination fix enhanced
- ✅ PyYAML optional dependency
- ✅ Comprehensive documentation

### v2.2.1 (Previous)
- Basic GRAG implementation
- Contamination fix (try/finally restoration)
- 41 experimental presets (0.56-0.64 range)
- Proven parameter ranges (0.1-2.0)

## 🎯 Use Cases

### Interior Design (Clean Room Workflow)
- Material changes
- Furniture adjustments
- Color variations
- Style transfers

### General Image Editing
- Object manipulation
- Attribute modification
- Composition adjustments
- Fine-grained control

### Research & Experimentation
- Attention mechanism analysis
- Parameter exploration
- Custom preset development
- Model behavior study

---

**⭐ Star this repository if you find it useful!**

**🐛 Report issues on [GitHub Issues](https://github.com/amir84ferdos/ComfyUI-GRAG/issues)**

**📧 Contact: Amir84ferdos@gmail.com**
