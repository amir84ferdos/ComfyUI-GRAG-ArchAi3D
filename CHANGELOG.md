# Changelog

All notable changes to the GRAG v3.0 project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-11-03

### Added
- **Simple Controller** - Beginner-friendly interface with 3 parameters
  - Preset dropdown (filtered to recommended presets)
  - Strength slider (proportional scaling from neutral)
  - Optional λ/δ override parameters
- **Unified Controller** - Advanced multi-mode interface
  - Simple mode (preset + manual λ/δ)
  - Advanced mode (per-layer control)
  - Expert mode (adaptive timestep + multi-resolution)
- **Advanced Sampler** - Enhanced KSampler with GRAG patches
  - v2.2.1 contamination fix (try/finally restoration)
  - Debug mode for attention analysis
  - Architecture auto-detection (Qwen/Flux/SD3)
- **Preset Manager** - Save/load/share custom presets
  - Save current parameters as named preset
  - Load user-saved presets
  - Delete user presets
  - YAML export functionality
- **54 Preset Library**
  - 41 v2.2.1 experimental presets (0.56-0.64 range)
  - 5 paper-recommended presets (0.95-1.15 range)
  - 3 Clean Room workflow presets
  - 3 v2.2.1 tested presets
  - 2 conservative presets
- **Core Algorithms**
  - `attention_v3.py` - Enhanced GRAG reweighting with per-layer support
  - `per_layer_control.py` - Layer-specific parameter control (4 strategies)
  - `adaptive_control.py` - Timestep-dependent scheduling (5 schedules)
  - `multi_resolution.py` - Multi-tier resolution system (paper's 2-tier)
  - `preset_loader.py` - YAML preset management with caching
- **Documentation**
  - README.md - Comprehensive package overview
  - INSTALL.md - Installation and troubleshooting
  - QUICK_START.md - Beginner's guide
  - SIMPLE_VS_UNIFIED.md - Controller comparison
  - STRENGTH_SLIDER_EXPLAINED.md - Strength slider mechanics
  - SIMPLE_CONTROLLER_UPDATES.md - Recent improvements
  - FIXES_APPLIED.md - Import fixes and troubleshooting

### Changed
- **Package Structure** - Modular architecture with separate core/ and nodes/ directories
- **Import System** - Relative imports for proper package structure
- **Strength Slider** - Now scales proportionally from neutral (1.0)
  - strength=0.0 → λ=1.0, δ=1.0 (neutral)
  - strength=1.0 → preset values (intended effect)
  - strength=2.0 → doubled deviation from neutral
- **PyYAML Dependency** - Made optional with hardcoded fallback
  - Works with 5 essential presets without PyYAML
  - Full 54-preset library with PyYAML installed
- **Preset Filtering** - Simple Controller shows only recommended presets

### Fixed
- **v2.2.1 Contamination Bug** - try/finally restoration prevents global state pollution
- **Import Errors** - Changed from absolute to relative imports
- **Strength Slider Bug** - Now produces intuitive scaling (was ineffective before)
- **PyYAML Import Errors** - Graceful fallback to hardcoded presets

### Technical Details
- **Python Version**: 3.8+
- **ComfyUI Compatibility**: Latest version
- **Total Nodes**: 4 (Simple Controller, Unified Controller, Advanced Sampler, Preset Manager)
- **Total Presets**: 54 (5 without PyYAML, 54 with PyYAML)
- **Total Code Lines**: ~3500 lines (nodes + core algorithms)
- **Total Documentation**: ~5000 lines

## [2.2.1] - Previous Release

### Added
- Basic GRAG implementation
- 41 experimental presets (0.56-0.64 range)
- Contamination fix (try/finally restoration)
- Parameter range validation (0.1-2.0)

### Known Issues
- Strength slider ineffective (multiplied metadata only, not λ/δ values)
- No beginner-friendly interface
- No per-layer control
- No adaptive timestep scheduling
- No multi-resolution support

## Migration Guide: v2.2.1 → v3.0.0

### For Users
1. **Install GRAG v3.0** in new folder: `ComfyUI/custom_nodes/GRAG/`
2. **Restart ComfyUI**
3. **Choose controller**:
   - Beginners → Use **Simple Controller**
   - Advanced → Use **Unified Controller** in "simple" mode
4. **Update workflows**:
   - Replace old GRAG nodes with new controllers
   - Use **GRAG Advanced Sampler** instead of standard KSampler

### Breaking Changes
- **Node names changed**: Old nodes won't be found
- **Metadata format**: v3.0 uses enhanced format (backward compatible)
- **Strength behavior**: Now scales proportionally (was ineffective before)

### Non-Breaking Changes
- **Presets**: All v2.2.1 presets imported and available
- **Parameter ranges**: Same (0.1-2.0 for λ and δ)
- **GRAG formula**: Unchanged (λ × k_bias + δ × Δk)

## Upgrade Instructions

### From v2.2.1 to v3.0.0

1. **Backup old workflows** (optional but recommended)
2. **Install v3.0.0** using one of these methods:
   - ComfyUI Manager: Search "GRAG" → Install
   - Git: `git clone https://github.com/amir84ferdos/ComfyUI-GRAG.git GRAG`
   - Manual: Download ZIP → Extract to `custom_nodes/GRAG/`
3. **Install PyYAML** (optional, for full preset library):
   ```bash
   pip install PyYAML
   ```
4. **Restart ComfyUI**
5. **Update workflows**:
   - Add **Simple Controller** or **Unified Controller**
   - Add **GRAG Advanced Sampler**
   - Remove old GRAG nodes
6. **Test** with "Paper: Balanced" preset at strength=1.0

### Recommended Starting Settings

**Beginners:**
```
Simple Controller:
├─ enable_grag: True
├─ preset: "Paper: Balanced"
├─ strength: 1.0
└─ lambda/delta_override: -1.0 (not used)
```

**Advanced Users:**
```
Unified Controller:
├─ enable_grag: True
├─ control_mode: "simple"
├─ preset: "Paper: Balanced"
├─ lambda_global: 1.05
├─ delta_global: 1.10
└─ strength_multiplier: 1.0
```

## Known Issues

### v3.0.0
- None currently known

### Reporting Issues
Please report bugs on [GitHub Issues](https://github.com/amir84ferdos/ComfyUI-GRAG/issues) with:
1. ComfyUI version
2. GRAG version (v3.0.0)
3. Console error messages
4. Steps to reproduce

## Roadmap

### v3.1.0 (Planned)
- [ ] Attention visualizer node
- [ ] Example workflows repository
- [ ] Video tutorials
- [ ] ComfyUI Manager integration

### v3.2.0 (Future)
- [ ] Real-time preview
- [ ] Batch processing support
- [ ] Performance optimizations
- [ ] Additional architectures (SDXL, etc.)

### Long-term
- [ ] GUI configuration tool
- [ ] Community preset sharing platform
- [ ] Integration with other editing tools
- [ ] Research paper publication

## Credits

### Contributors
- **Amir Ferdos** (ArchAi3d) - Main developer

### Based On
- [arXiv 2510.24657](https://arxiv.org/abs/2510.24657) - GRAG-Image-Editing paper
- [little-misfit's repository](https://github.com/little-misfit/GRAG-Image-Editing) - Original implementation
- v2.2.1 learnings - Production experience

### Special Thanks
- ComfyUI community for feedback and testing
- Research paper authors for the GRAG technique
- All users who contributed preset configurations

## License

MIT License - See [LICENSE](LICENSE) for full text

---

**Last Updated**: 2025-11-03
**Current Version**: v3.0.0
**Status**: Stable
