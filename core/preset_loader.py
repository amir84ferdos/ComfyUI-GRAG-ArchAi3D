"""
Preset Loader Utility

Loads GRAG presets from YAML files and provides a unified interface
for accessing preset configurations.

Author: Amir Ferdos (ArchAi3d)
License: MIT
"""

import os
from typing import Dict, List

# Try to import yaml, but provide fallback if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("[GRAG Preset Loader] Warning: PyYAML not installed. Using hardcoded presets.")


class PresetLoader:
    """Manages loading and caching of GRAG presets from YAML files."""

    def __init__(self):
        self.presets_cache = {}
        self.presets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets")
        self._load_all_presets()

    def _load_all_presets(self):
        """Load all presets from YAML files or use hardcoded fallback."""
        if HAS_YAML and os.path.exists(self.presets_dir):
            # Try to load from YAML files
            preset_files = [
                "v221_experimental.yaml",
                "paper_stable.yaml",
            ]

            for filename in preset_files:
                filepath = os.path.join(self.presets_dir, filename)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                            if data and 'presets' in data:
                                # Merge presets from this file
                                self.presets_cache.update(data['presets'])
                    except Exception as e:
                        print(f"[GRAG Preset Loader] Error loading {filename}: {e}")

        # If YAML loading failed or YAML not available, use hardcoded presets
        if len(self.presets_cache) == 0:
            print("[GRAG Preset Loader] Using hardcoded presets (install PyYAML for full preset library)")
            self.presets_cache = self._get_hardcoded_presets()

        print(f"[GRAG Preset Loader] Loaded {len(self.presets_cache)} presets")

    def _get_hardcoded_presets(self) -> Dict:
        """Fallback hardcoded presets when YAML is not available."""
        return {
            "custom": {
                "name": "Custom",
                "lambda": 1.0,
                "delta": 1.0,
                "strength": 1.0,
                "description": "Manual control - adjust all parameters yourself",
                "category": "manual"
            },
            "paper_balanced": {
                "name": "Paper: Balanced",
                "lambda": 1.05,
                "delta": 1.10,
                "strength": 1.0,
                "description": "Recommended starting point (paper validated)",
                "category": "paper_stable"
            },
            "paper_subtle": {
                "name": "Paper: Subtle",
                "lambda": 1.00,
                "delta": 1.05,
                "strength": 1.0,
                "description": "Subtle edit within paper's stable range",
                "category": "paper_stable"
            },
            "v221_balanced": {
                "name": "v2.2.1: Balanced",
                "lambda": 1.00,
                "delta": 1.50,
                "strength": 1.0,
                "description": "v2.2.1 proven range for visible effects",
                "category": "v221_proven"
            },
            "clean_room_gentle": {
                "name": "Clean Room: Gentle",
                "lambda": 0.85,
                "delta": 1.15,
                "strength": 1.0,
                "description": "Window preservation, gentle scaffolding removal",
                "category": "clean_room"
            },
        }

    def get_preset(self, preset_key: str) -> Dict:
        """Get preset configuration by key.

        Args:
            preset_key: Preset identifier (e.g., "preset_01", "paper_balanced")

        Returns:
            dict: Preset configuration with lambda, delta, strength, etc.
        """
        preset = self.presets_cache.get(preset_key)
        if preset is None:
            print(f"[GRAG Preset Loader] Warning: Preset '{preset_key}' not found, using custom")
            return self.presets_cache.get("custom", {
                "name": "Custom",
                "lambda": 1.0,
                "delta": 1.05,
                "strength": 1.0,
                "description": "Manual control"
            })
        return preset

    def get_all_preset_names(self) -> List[str]:
        """Get list of all available preset display names.

        Returns:
            list: List of preset names for dropdown
        """
        # Sort presets: custom first, then by category
        presets_list = []

        # Custom first
        if "custom" in self.presets_cache:
            presets_list.append(self.presets_cache["custom"]["name"])

        # Paper stable
        for key, preset in self.presets_cache.items():
            if key != "custom" and preset.get("category") == "paper_stable":
                presets_list.append(preset["name"])

        # v2.2.1 proven
        for key, preset in self.presets_cache.items():
            if preset.get("category") == "v221_proven":
                presets_list.append(preset["name"])

        # Clean room
        for key, preset in self.presets_cache.items():
            if preset.get("category") == "clean_room":
                presets_list.append(preset["name"])

        # v2.2.1 experimental (sorted numerically)
        experimental_presets = []
        for key, preset in self.presets_cache.items():
            if preset.get("category") == "v221_experimental":
                experimental_presets.append((key, preset["name"]))

        # Sort experimental by preset number
        experimental_presets.sort(key=lambda x: int(x[0].split('_')[1]) if '_' in x[0] else 0)
        for _, name in experimental_presets:
            presets_list.append(name)

        # Conservative
        for key, preset in self.presets_cache.items():
            if preset.get("category") == "conservative":
                presets_list.append(preset["name"])

        return presets_list

    def get_preset_by_name(self, name: str) -> Dict:
        """Get preset configuration by display name.

        Args:
            name: Preset display name (e.g., "Paper: Balanced", "Preset 01")

        Returns:
            dict: Preset configuration
        """
        for key, preset in self.presets_cache.items():
            if preset.get("name") == name:
                return preset

        # Fallback to custom
        return self.get_preset("custom")


# Global preset loader instance
_preset_loader = None


def get_preset_loader() -> PresetLoader:
    """Get global preset loader instance (singleton)."""
    global _preset_loader
    if _preset_loader is None:
        _preset_loader = PresetLoader()
    return _preset_loader


__all__ = [
    "PresetLoader",
    "get_preset_loader",
]
