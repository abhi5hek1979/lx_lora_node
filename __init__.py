from .lx_lora_node import (
    LevelX_MultiAutoLoRA, 
    LevelX_FluxAutoLoRA, 
    LevelX_SDXLAutoLoRA,
    LevelX_Flux2AutoLoRA,
    LevelX_QwenAutoLoRA,
    LevelX_ZImageAutoLoRA,
    LevelX_TriggerSaver
)

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
    "LevelX_ZImageAutoLoRA": "🧿 Level X Auto-LoRA (Z-Image)",
    "LevelX_TriggerSaver": "💾 Level X Trigger Manager"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']