"""
Advanced GRAG (Group-Relative Attention Guidance) Package v3.0

A standalone ComfyUI package implementing advanced GRAG attention control
with per-layer, adaptive, and multi-resolution support.

Based on:
- arXiv 2510.24657 (GRAG paper)
- v2.2.1 implementation learnings
- Production experience and user feedback

Features:
- Unified controller interface (simple → advanced modes)
- Per-layer λ/δ control for precision editing
- Adaptive timestep scheduling
- Multi-resolution tier support (paper's 2-tier system)
- Preset management (save/load/share)
- Attention visualization for debugging
- Architecture auto-detection (Qwen/Flux/SD3/etc)

Author: Amir Ferdos (ArchAi3d)
Email: Amir84ferdos@gmail.com
LinkedIn: https://www.linkedin.com/in/archai3d/
GitHub: https://github.com/amir84ferdos
Version: 3.0.0
License: MIT
"""

try:
    from .nodes.grag_simple_controller import GRAGSimpleController
    from .nodes.grag_unified_controller import GRAGUnifiedController
    from .nodes.grag_advanced_sampler import GRAGAdvancedSampler
    from .nodes.grag_preset_manager import GRAGPresetManager

    NODES_LOADED = True
except Exception as e:
    print(f"[GRAG v3.0] Warning: Error loading nodes: {e}")
    import traceback
    traceback.print_exc()
    NODES_LOADED = False
    GRAGSimpleController = None
    GRAGUnifiedController = None
    GRAGAdvancedSampler = None
    GRAGPresetManager = None

# ============================================================================
# COMFYUI NODE REGISTRATION
# ============================================================================

if NODES_LOADED:
    NODE_CLASS_MAPPINGS = {
        "GRAG_Simple_Controller": GRAGSimpleController,
        "GRAG_Unified_Controller": GRAGUnifiedController,
        "GRAG_Advanced_Sampler": GRAGAdvancedSampler,
        "GRAG_Preset_Manager": GRAGPresetManager,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "GRAG_Simple_Controller": "🎛️ GRAG Simple Controller v3.0",
        "GRAG_Unified_Controller": "🎚️ GRAG Unified Controller v3.0",
        "GRAG_Advanced_Sampler": "⚙️ GRAG Advanced Sampler v3.0",
        "GRAG_Preset_Manager": "💾 GRAG Preset Manager v3.0",
    }
else:
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
    print("[GRAG v3.0] ERROR: Nodes failed to load. Check error messages above.")

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'GRAGSimpleController',
    'GRAGUnifiedController',
    'GRAGAdvancedSampler',
    'GRAGPresetManager',
]

__version__ = "3.0.0"
__author__ = "Amir Ferdos (ArchAi3d)"

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

print("=" * 70)
print(f"[GRAG v{__version__}] Advanced GRAG Package Loading...")
print(f"  🎛️ Simple Controller: Beginner-friendly preset-based control")
print(f"  🎚️ Unified Controller: Simple → Advanced → Expert modes")
print(f"  ⚙️ Advanced Sampler: Per-layer + Adaptive + Multi-res")
print(f"  💾 Preset Manager: Save/Load/Share configurations")
print(f"  📚 Imported: 41 v2.2.1 presets + Paper-recommended")
print(f"  ✅ Total: {len(NODE_CLASS_MAPPINGS)} nodes loaded!")
print(f"")
print(f"  🚀 Beginner: [Encoder] → [GRAG Simple Controller] → [GRAG Advanced Sampler]")
print(f"  🎓 Advanced: [Encoder] → [GRAG Unified Controller] → [GRAG Advanced Sampler]")
print(f"  🔧 Presets: Use preset dropdown or 'Custom' for manual control")
print(f"  📚 Documentation: ./docs/QUICK_START.md")
print(f"  ⚖️  License: MIT (Free for all uses)")
print("=" * 70)
