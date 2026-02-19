import os
import json
import folder_paths
from .lx_lora_node import (
    LevelX_MultiAutoLoRA, 
    LevelX_FluxAutoLoRA, 
    LevelX_SDXLAutoLoRA,
    LevelX_Flux2AutoLoRA,
    LevelX_QwenAutoLoRA,
    LevelX_ZImageAutoLoRA,
    LevelX_TriggerSaver
)

def patch_pysssss_settings():
    """Silently injects Level X nodes into the Pythongosssss LoRA Info settings on boot."""
    try:
        user_dir = os.path.join(folder_paths.base_path, "user")
        if not os.path.exists(user_dir):
            return

        lx_nodes = [
            "LevelX_MultiAutoLoRA.lora_1_name", "LevelX_MultiAutoLoRA.lora_2_name", "LevelX_MultiAutoLoRA.lora_3_name",
            "LevelX_FluxAutoLoRA.lora_1_name", "LevelX_FluxAutoLoRA.lora_2_name", "LevelX_FluxAutoLoRA.lora_3_name",
            "LevelX_SDXLAutoLoRA.lora_1_name", "LevelX_SDXLAutoLoRA.lora_2_name", "LevelX_SDXLAutoLoRA.lora_3_name",
            "LevelX_Flux2AutoLoRA.lora_1_name", "LevelX_Flux2AutoLoRA.lora_2_name", "LevelX_Flux2AutoLoRA.lora_3_name",
            "LevelX_QwenAutoLoRA.lora_1_name", "LevelX_QwenAutoLoRA.lora_2_name", "LevelX_QwenAutoLoRA.lora_3_name",
            "LevelX_ZImageAutoLoRA.lora_1_name", "LevelX_ZImageAutoLoRA.lora_2_name", "LevelX_ZImageAutoLoRA.lora_3_name"
        ]
# Iterate through all ComfyUI user profiles (usually 'default')
        for profile in os.listdir(user_dir):
            profile_path = os.path.join(user_dir, profile)
            if not os.path.isdir(profile_path):
                continue
                
            settings_path = os.path.join(profile_path, "comfy.settings.json")
            if not os.path.exists(settings_path):
                continue
                
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            key = "pysssss.ModelInfo.LoraNodesWidgets"
            if key in settings:
                current_val = settings[key]
                needs_update = False
                
                for node in lx_nodes:
                    if node not in current_val:
                        current_val += f",{node}"
                        needs_update = True
                        
                if needs_update:
                    settings[key] = current_val
                    with open(settings_path, "w", encoding="utf-8") as f:
                        json.dump(settings, f, indent=4)
                    print(f"[Level X] ✨ Auto-patched Pythongosssss settings for profile: {profile}")
                    
    except Exception as e:
        print(f"[Level X] ⚠️ Non-critical: Could not auto-patch Pythongosssss settings: {e}")

# Run the patcher once when the node is initialized
patch_pysssss_settings()
NODE_CLASS_MAPPINGS = {
    "LevelX_MultiAutoLoRA": LevelX_MultiAutoLoRA,
    "LevelX_FluxAutoLoRA": LevelX_FluxAutoLoRA,
    "LevelX_SDXLAutoLoRA": LevelX_SDXLAutoLoRA,
    "LevelX_Flux2AutoLoRA": LevelX_Flux2AutoLoRA,
    "LevelX_QwenAutoLoRA": LevelX_QwenAutoLoRA,
    "LevelX_ZImageAutoLoRA": LevelX_ZImageAutoLoRA,
    "LevelX_TriggerSaver": LevelX_TriggerSaver
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LevelX_MultiAutoLoRA": "🔥 Level X Auto-LoRA (Universal)",
    "LevelX_FluxAutoLoRA": "⚡ Level X Auto-LoRA (FLUX)",
    "LevelX_SDXLAutoLoRA": "🎨 Level X Auto-LoRA (SDXL)",
    "LevelX_Flux2AutoLoRA": "🌀 Level X Auto-LoRA (FLUX 2)",
    "LevelX_QwenAutoLoRA": "👾 Level X Auto-LoRA (Qwen)",
    "LevelX_ZImageAutoLoRA": "🖼️ Level X Auto-LoRA (Z-Image)",
    "LevelX_TriggerSaver": "💾 Level X Trigger Manager"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']