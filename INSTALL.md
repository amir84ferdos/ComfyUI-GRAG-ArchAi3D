# GRAG v3.0 - Installation Guide

## ✅ Basic Installation

The GRAG v3.0 package works with 5 essential presets without any additional dependencies!

### Installation Location
```
ComfyUI/custom_nodes/GRAG/
```

### To Use
1. **Restart ComfyUI** (if it's running)
2. **Find nodes:** Right-click → Add Node → Search "GRAG"
3. **You'll see:**
   - 🎛️ GRAG Simple Controller v3.0
   - 🎚️ GRAG Unified Controller v3.0
   - ⚙️ GRAG Advanced Sampler v3.0
   - 💾 GRAG Preset Manager v3.0

### Available Presets (Without PyYAML)
- Custom (manual control)
- Paper: Balanced ⭐ (Recommended)
- Paper: Subtle
- v2.2.1: Balanced
- Clean Room: Gentle

---

## 🎯 Full Installation (Recommended - Get All 54 Presets!)

To unlock all 54 presets (41 v2.2.1 + 13 paper/proven), install PyYAML:

### Option 1: Using pip (Recommended)
```bash
# Navigate to ComfyUI directory
cd ComfyUI

# Install PyYAML
pip install PyYAML

# Or install from requirements.txt
pip install -r custom_nodes/GRAG/requirements.txt
```

### Option 2: Using ComfyUI's Embedded Python
```bash
# If ComfyUI uses embedded Python
python_embeded/python.exe -m pip install PyYAML
```

### Option 3: Using conda (if applicable)
```bash
conda install pyyaml
```

### Verify Installation
After installing PyYAML, restart ComfyUI and check the console:
```
[GRAG Preset Loader] Loaded 54 presets  ← Should show 54, not 5!
```

---

## 🔧 Troubleshooting

### Problem: Nodes don't appear in ComfyUI menu

**Solution 1: Check Console for Errors**
Look for error messages when ComfyUI starts:
```
[GRAG v3.0] Warning: Error loading nodes: ...
```

**Solution 2: Verify Package Location**
```bash
# Windows
dir ComfyUI\custom_nodes\GRAG

# Linux/Mac
ls ComfyUI/custom_nodes/GRAG
```
You should see:
- __init__.py
- nodes/
- core/
- presets/
- docs/

**Solution 3: Check Python Path**
Make sure ComfyUI can find the package. The `__init__.py` should have:
```python
try:
    from .nodes.grag_unified_controller import GRAGUnifiedController
    # ...
    NODES_LOADED = True
except Exception as e:
    print(f"[GRAG v3.0] Warning: Error loading nodes: {e}")
```

**Solution 4: Restart ComfyUI**
- Close ComfyUI completely
- Restart it
- Check console output

---

### Problem: Only 5 presets available instead of 54

**Cause:** PyYAML is not installed

**Solution:** Install PyYAML using one of the methods above

**Console Message:**
```
[GRAG Preset Loader] Warning: PyYAML not installed. Using hardcoded presets.
[GRAG Preset Loader] Using hardcoded presets (install PyYAML for full preset library)
[GRAG Preset Loader] Loaded 5 presets
```

**After Installing PyYAML:**
```
[GRAG Preset Loader] Loaded 54 presets
```

---

### Problem: Import errors in console

**Check for:**
```
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'comfy'
```

**Cause:** These are normal - GRAG uses ComfyUI's built-in modules

**What to look for instead:**
- Errors about missing files
- Syntax errors
- Import errors from GRAG's own files

---

### Problem: GRAG effects not visible

**Check:**
1. ✅ Using **GRAG Advanced Sampler**, not standard KSampler
2. ✅ `enable_grag: True` in Unified Controller
3. ✅ Preset with λ≠1.0 or δ≠1.0 (not "Custom" with default values)
4. ✅ Console shows "Patched 60 Attention layers"

**If still no effect:**
- Try "v2.2.1: Balanced" preset (λ=1.0, δ=1.5) for obvious effects
- Check console for error messages during sampling

---

## 📋 Installation Checklist

### Basic (Works Without PyYAML)
- [x] Package in correct location
- [ ] ComfyUI restarted
- [ ] Nodes appear in menu (search "GRAG")
- [ ] Can add nodes to canvas
- [ ] 5 presets available in dropdown

### Full (With PyYAML)
- [ ] PyYAML installed (`pip install PyYAML`)
- [ ] ComfyUI restarted after installation
- [ ] Console shows "Loaded 54 presets"
- [ ] All presets visible in dropdown

### Functional
- [ ] Basic workflow completes without errors
- [ ] Console shows "Patched 60 Attention layers"
- [ ] GRAG effects visible (compare enable_grag True vs False)

---

## 🚀 Quick Test Workflow

After installation, test with this simple workflow:

```
[Load Image]
    ↓
[Qwen Encoder V2]
    ↓
[GRAG Unified Controller v3.0]
├─ enable_grag: True
├─ control_mode: "simple"
├─ preset: "Paper: Balanced"  ← Start here!
    ↓
[GRAG Advanced Sampler v3.0]
├─ steps: 20
├─ cfg: 8.0
├─ sampler: euler
    ↓
[VAE Decode]
    ↓
[Save Image]
```

**Expected Console Output:**
```
[GRAG v3.0.0] Advanced GRAG Package Loading...
  🎚️ Unified Controller: Simple → Advanced modes
  ⚙️ Advanced Sampler: Per-layer + Adaptive + Multi-res
  💾 Preset Manager: Save/Load/Share configurations
  📚 Imported: 41 v2.2.1 presets + Paper-recommended
  ✅ Total: 3 nodes loaded!

[GRAG v3.0] Simple Mode - Preset: Paper: Balanced
[GRAG v3.0] Parameters: λ=1.05, δ=1.10, strength=1.00
[GRAG v3.0] GRAG enabled - Global: λ=1.05, δ=1.10, strength=1.00
[GRAG v3.0] Patched 60 Attention layers
[GRAG v3.0] GRAG patches injected successfully
```

---

## 💾 Optional: Install PyYAML for Full Features

### Why Install PyYAML?

**Without PyYAML (5 presets):**
- Custom
- Paper: Balanced
- Paper: Subtle
- v2.2.1: Balanced
- Clean Room: Gentle

**With PyYAML (54 presets):**
- All of the above +
- 41 v2.2.1 experimental presets (Preset 01-41)
- 5 paper-recommended presets
- 3 Clean Room presets
- 2 conservative presets
- User-saved custom presets (via Preset Manager)

### Installation Commands

**Windows (ComfyUI standalone):**
```bash
cd ComfyUI
pip install PyYAML
```

**Windows (Python embedded):**
```bash
python_embeded/python.exe -m pip install PyYAML
```

**Linux/Mac:**
```bash
pip install PyYAML
# or
pip3 install PyYAML
```

---

## 📞 Support

**Still having issues?**

1. **Check console output** when ComfyUI starts
2. **Look for error messages** in red
3. **Share error messages** for help:
   - GitHub: https://github.com/amir84ferdos/ComfyUI-ArchAi3d-Qwen
   - Email: Amir84ferdos@gmail.com

**Common fixes:**
- Restart ComfyUI
- Verify package location
- Install PyYAML (optional but recommended)
- Check Python environment

---

## 📚 Next Steps

After successful installation:

1. **Read Quick Start:** `docs/QUICK_START.md`
2. **Try basic workflow** with "Paper: Balanced" preset
3. **Experiment** with different presets
4. **Install PyYAML** for full preset library (optional)
5. **Share feedback!**

---

**Version:** 3.0.0
**Status:** Ready to use (5 presets) | Full features with PyYAML (54 presets)
**License:** MIT (Free for all uses)
