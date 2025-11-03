"""
GRAG Preset Manager Node v3.0

Node for saving, loading, and managing GRAG presets.

Features:
- Save current parameters as custom preset
- Load user-saved presets
- Delete user presets
- Export preset to YAML file
- Share presets with community

Author: Amir Ferdos (ArchAi3d)
Email: Amir84ferdos@gmail.com
License: MIT
"""

import os
from datetime import datetime

# Use relative imports for package structure
from ..core.preset_loader import get_preset_loader

# PyYAML is optional - will be handled by preset_loader
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("[GRAG Preset Manager] Warning: PyYAML not installed. Save/load functionality will be limited.")


class GRAGPresetManager:
    """Preset Manager for saving/loading/managing GRAG configurations.

    Allows users to:
    - Save current GRAG parameters as named preset
    - Load saved presets
    - Delete user presets
    - Export presets to share

    Version: 3.0.0
    """

    def __init__(self):
        self.preset_loader = get_preset_loader()
        self.user_presets_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "presets",
            "user_custom.yaml"
        )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Operation mode
                "mode": (["save", "load", "delete", "info"], {
                    "default": "info",
                    "tooltip": "Save: Create new preset | Load: Get preset params | Delete: Remove preset | Info: Show details"
                }),

                # Preset name
                "preset_name": ("STRING", {
                    "default": "my_preset",
                    "multiline": False,
                    "tooltip": "Name for your custom preset"
                }),
            },
            "optional": {
                # Parameters to save (for save mode)
                "lambda_value": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Lambda value to save"
                }),
                "delta_value": ("FLOAT", {
                    "default": 1.05,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Delta value to save"
                }),
                "strength_value": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Strength value to save"
                }),
                "description": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Description of this preset"
                }),
                "category": ("STRING", {
                    "default": "user_custom",
                    "multiline": False,
                    "tooltip": "Category for organization"
                }),
                "use_case": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Use case description"
                }),
            }
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("lambda", "delta", "strength", "info")
    FUNCTION = "manage_preset"
    CATEGORY = "GRAG/v3.0"

    def manage_preset(
        self,
        mode,
        preset_name,
        lambda_value=1.0,
        delta_value=1.05,
        strength_value=1.0,
        description="",
        category="user_custom",
        use_case=""
    ):
        """Manage GRAG presets based on selected mode.

        Args:
            mode: Operation mode (save/load/delete/info)
            preset_name: Name of preset
            lambda_value: Lambda parameter (for save)
            delta_value: Delta parameter (for save)
            strength_value: Strength parameter (for save)
            description: Preset description (for save)
            category: Preset category (for save)
            use_case: Use case description (for save)

        Returns:
            tuple: (lambda, delta, strength, info_message)
        """
        if mode == "save":
            return self._save_preset(
                preset_name,
                lambda_value,
                delta_value,
                strength_value,
                description,
                category,
                use_case
            )
        elif mode == "load":
            return self._load_preset(preset_name)
        elif mode == "delete":
            return self._delete_preset(preset_name)
        elif mode == "info":
            return self._show_info(preset_name)
        else:
            return (1.0, 1.05, 1.0, f"Unknown mode: {mode}")

    def _save_preset(self, name, lambda_val, delta_val, strength, description, category, use_case):
        """Save a new custom preset.

        Args:
            name: Preset name
            lambda_val: Lambda parameter
            delta_val: Delta parameter
            strength: Strength parameter
            description: Preset description
            category: Preset category
            use_case: Use case description

        Returns:
            tuple: (lambda, delta, strength, info_message)
        """
        if not HAS_YAML:
            error_msg = "❌ PyYAML not installed. Cannot save presets.\nInstall PyYAML: pip install PyYAML"
            print(f"[GRAG Preset Manager] {error_msg}")
            return (lambda_val, delta_val, strength, error_msg)

        try:
            # Load existing user presets
            user_presets = {}
            if os.path.exists(self.user_presets_file):
                with open(self.user_presets_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'presets' in data:
                        user_presets = data['presets']

            # Create preset key (lowercase, replace spaces with underscores)
            preset_key = name.lower().replace(' ', '_').replace('-', '_')

            # Create preset entry
            user_presets[preset_key] = {
                "name": name,
                "lambda": float(lambda_val),
                "delta": float(delta_val),
                "strength": float(strength),
                "description": description or f"Custom preset: {name}",
                "category": category,
                "use_case": use_case or "user-defined",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Save to YAML
            output_data = {
                "presets": user_presets,
                "metadata": {
                    "version": "3.0.0",
                    "total_presets": len(user_presets),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            }

            with open(self.user_presets_file, 'w', encoding='utf-8') as f:
                yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)

            info_msg = f"✅ Saved preset '{name}' successfully!\n"
            info_msg += f"λ={lambda_val:.2f}, δ={delta_val:.2f}, strength={strength:.2f}\n"
            info_msg += f"File: user_custom.yaml"

            print(f"[GRAG Preset Manager] {info_msg}")

            return (lambda_val, delta_val, strength, info_msg)

        except Exception as e:
            error_msg = f"❌ Error saving preset: {e}"
            print(f"[GRAG Preset Manager] {error_msg}")
            return (lambda_val, delta_val, strength, error_msg)

    def _load_preset(self, name):
        """Load a preset by name.

        Args:
            name: Preset name (display name)

        Returns:
            tuple: (lambda, delta, strength, info_message)
        """
        try:
            # Try to load from preset loader
            preset = self.preset_loader.get_preset_by_name(name)

            if preset:
                lambda_val = preset.get("lambda", 1.0)
                delta_val = preset.get("delta", 1.05)
                strength = preset.get("strength", 1.0)
                description = preset.get("description", "")
                category = preset.get("category", "")

                info_msg = f"✅ Loaded preset '{name}'\n"
                info_msg += f"λ={lambda_val:.2f}, δ={delta_val:.2f}, strength={strength:.2f}\n"
                info_msg += f"Category: {category}\n"
                info_msg += f"Description: {description}"

                print(f"[GRAG Preset Manager] {info_msg}")

                return (lambda_val, delta_val, strength, info_msg)
            else:
                error_msg = f"❌ Preset '{name}' not found"
                print(f"[GRAG Preset Manager] {error_msg}")
                return (1.0, 1.05, 1.0, error_msg)

        except Exception as e:
            error_msg = f"❌ Error loading preset: {e}"
            print(f"[GRAG Preset Manager] {error_msg}")
            return (1.0, 1.05, 1.0, error_msg)

    def _delete_preset(self, name):
        """Delete a user preset.

        Args:
            name: Preset name

        Returns:
            tuple: (lambda, delta, strength, info_message)
        """
        if not HAS_YAML:
            error_msg = "❌ PyYAML not installed. Cannot delete presets.\nInstall PyYAML: pip install PyYAML"
            print(f"[GRAG Preset Manager] {error_msg}")
            return (1.0, 1.05, 1.0, error_msg)

        try:
            # Load existing user presets
            if not os.path.exists(self.user_presets_file):
                error_msg = f"❌ No user presets file found"
                return (1.0, 1.05, 1.0, error_msg)

            with open(self.user_presets_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or 'presets' not in data:
                error_msg = f"❌ No user presets found"
                return (1.0, 1.05, 1.0, error_msg)

            user_presets = data['presets']

            # Find preset key
            preset_key = name.lower().replace(' ', '_').replace('-', '_')

            # Alternative: search by name
            found_key = None
            for key, preset in user_presets.items():
                if preset.get("name") == name or key == preset_key:
                    found_key = key
                    break

            if found_key:
                deleted_preset = user_presets[found_key]
                del user_presets[found_key]

                # Save updated presets
                output_data = {
                    "presets": user_presets,
                    "metadata": {
                        "version": "3.0.0",
                        "total_presets": len(user_presets),
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                }

                with open(self.user_presets_file, 'w', encoding='utf-8') as f:
                    yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)

                info_msg = f"✅ Deleted preset '{name}' successfully"
                print(f"[GRAG Preset Manager] {info_msg}")

                return (1.0, 1.05, 1.0, info_msg)
            else:
                error_msg = f"❌ Preset '{name}' not found in user presets"
                return (1.0, 1.05, 1.0, error_msg)

        except Exception as e:
            error_msg = f"❌ Error deleting preset: {e}"
            print(f"[GRAG Preset Manager] {error_msg}")
            return (1.0, 1.05, 1.0, error_msg)

    def _show_info(self, name):
        """Show detailed information about a preset.

        Args:
            name: Preset name

        Returns:
            tuple: (lambda, delta, strength, info_message)
        """
        try:
            preset = self.preset_loader.get_preset_by_name(name)

            if preset:
                lambda_val = preset.get("lambda", 1.0)
                delta_val = preset.get("delta", 1.05)
                strength = preset.get("strength", 1.0)
                description = preset.get("description", "N/A")
                category = preset.get("category", "N/A")
                use_case = preset.get("use_case", "N/A")
                created = preset.get("created", "N/A")

                info_msg = f"📊 Preset Information: '{name}'\n"
                info_msg += f"=" * 50 + "\n"
                info_msg += f"Parameters:\n"
                info_msg += f"  λ (lambda): {lambda_val:.2f}\n"
                info_msg += f"  δ (delta):  {delta_val:.2f}\n"
                info_msg += f"  Strength:   {strength:.2f}\n"
                info_msg += f"\n"
                info_msg += f"Metadata:\n"
                info_msg += f"  Category:    {category}\n"
                info_msg += f"  Use Case:    {use_case}\n"
                info_msg += f"  Description: {description}\n"
                if created != "N/A":
                    info_msg += f"  Created:     {created}\n"

                print(f"[GRAG Preset Manager]\n{info_msg}")

                return (lambda_val, delta_val, strength, info_msg)
            else:
                error_msg = f"❌ Preset '{name}' not found"
                return (1.0, 1.05, 1.0, error_msg)

        except Exception as e:
            error_msg = f"❌ Error showing info: {e}"
            return (1.0, 1.05, 1.0, error_msg)


# ============================================================================
# COMFYUI NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "GRAG_Preset_Manager": GRAGPresetManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRAG_Preset_Manager": "💾 GRAG Preset Manager v3.0"
}
