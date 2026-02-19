import folder_paths
import comfy.sd
import comfy.utils
import os
import json
import urllib.parse
import urllib.request
from safetensors import safe_open

# ==============================================================================
#  SHARED UTILS
# ==============================================================================
def get_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "lora_trigger.json")

def load_db():
    path = get_db_path()
    if not os.path.exists(path): return {}
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_db(db):
    try:
        with open(get_db_path(), 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4)
        print(f"[Level X] 💾 DB Saved ({len(db)} entries)")
    except Exception as e:
        print(f"[Level X] ❌ Save Failed: {e}")

def get_filtered_loras(prefix=None):
    all_loras = folder_paths.get_filename_list("loras")
    if not prefix: 
        return ["None"] + all_loras
    
    filtered = [
        x for x in all_loras 
        if x.lower().startswith(prefix.lower() + "/") 
        or x.lower().startswith(prefix.lower() + "\\")
    ]
    return ["None"] + filtered

# ==============================================================================
#  BASE CLASS (Logic Engine)
# ==============================================================================
class LevelX_BaseAutoLoRA:
    def __init__(self):
        pass

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "final_prompt", "triggers_added")
    FUNCTION = "apply_lora_stack"
    CATEGORY = "Level X/Loaders"

    def get_trigger(self, lora_name, db):
        if not lora_name or lora_name == "None": return None
        input_full = lora_name.replace("\\", "/").strip().lower()
        input_leaf = input_full.split("/")[-1]

        for db_key, trigger in db.items():
            k_full = db_key.replace("\\", "/").strip().lower()
            k_leaf = k_full.split("/")[-1]
            if input_full == k_full or input_leaf == k_leaf:
                return trigger
        return None
    def apply_lora_stack(self, model, clip, prompt, 
                         lora_1_name, lora_1_strength, lora_1_mode, lora_1_config,
                         lora_2_name, lora_2_strength, lora_2_mode, lora_2_config,
                         lora_3_name, lora_3_strength, lora_3_mode, lora_3_config,
                         optional_model_stack=None, optional_clip_stack=None):

        current_model = optional_model_stack if optional_model_stack else model
        current_clip = optional_clip_stack if optional_clip_stack else clip
        db = load_db()
        
        prefix_trigger = ""
        suffix_triggers = []
        all_injected = []

        # Isolated Configuration per LoRA
        stack_config = [
            (lora_1_name, lora_1_strength, lora_1_mode, lora_1_config, True),
            (lora_2_name, lora_2_strength, lora_2_mode, lora_2_config, False),
            (lora_3_name, lora_3_strength, lora_3_mode, lora_3_config, False)
        ]

        for name, strength, mode, config, is_first in stack_config:
            if name == "None" or strength == 0: continue
            
            lora_path = folder_paths.get_full_path("loras", name)
            if lora_path:
                print(f"[Level X] Loading: {name}")
                lora_obj = comfy.utils.load_torch_file(lora_path, safe_load=True)
                current_model, current_clip = comfy.sd.load_lora_for_models(
                    current_model, current_clip, lora_obj, strength, strength
                )
            
            # Independent Trigger Logic
            trig = ""
            if mode == "Custom Override":
                trig = config.strip()
            elif mode != "None":
                db_trig = self.get_trigger(name, db)
                if db_trig:
                    if mode == "All":
                        trig = db_trig
                    else:
                        trig_list = [t.strip() for t in db_trig.split(",") if t.strip()]
                        selected = []
                        if mode == "First" and trig_list:
                            selected.append(trig_list[0])
                        elif mode == "By Index":
                            try:
                                indices = [int(i.strip()) - 1 for i in config.split(",")]
                                for idx in indices:
                                    if 0 <= idx < len(trig_list):
                                        selected.append(trig_list[idx])
                            except:
                                selected = trig_list # Fallback on error
                        trig = ", ".join(selected)

            if trig:
                prompt_has_it = trig.lower() in prompt.lower()
                already_added = trig in all_injected or trig == prefix_trigger
                if not prompt_has_it and not already_added:
                    if is_first: prefix_trigger = trig
                    else: suffix_triggers.append(trig)
                    all_injected.append(trig)

        parts = []
        if prefix_trigger: parts.append(prefix_trigger)
        if prompt.strip(): parts.append(prompt.strip())
        if suffix_triggers: parts.append(", ".join(suffix_triggers))
            
        final_prompt = ", ".join(parts).replace(" ,", ",").replace(",,", ",")
        return (current_model, current_clip, final_prompt, ", ".join(all_injected))
# ==============================================================================
#  VARIANT 1: UNIVERSAL
# ==============================================================================
class LevelX_MultiAutoLoRA(LevelX_BaseAutoLoRA):
    @classmethod
    def INPUT_TYPES(s):
        lst = get_filtered_loras(None)
        modes = ["All", "First", "By Index", "Custom Override", "None"]
        return {
            "required": {
                "model": ("MODEL",), "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "lora_1_name": (lst, ), "lora_1_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_1_mode": (modes, {"default": "All"}), "lora_1_config": ("STRING", {"default": "1"}),
                "lora_2_name": (lst, ), "lora_2_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_2_mode": (modes, {"default": "All"}), "lora_2_config": ("STRING", {"default": "1"}),
                "lora_3_name": (lst, ), "lora_3_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_3_mode": (modes, {"default": "All"}), "lora_3_config": ("STRING", {"default": "1"}),
            },
            "optional": { "optional_model_stack": ("MODEL",), "optional_clip_stack": ("CLIP",), }
        }

# ==============================================================================
#  VARIANT 2: FLUX ONLY
# ==============================================================================
class LevelX_FluxAutoLoRA(LevelX_BaseAutoLoRA):
    @classmethod
    def INPUT_TYPES(s):
        lst = get_filtered_loras("FLUX")
        modes = ["All", "First", "By Index", "Custom Override", "None"]
        return {
            "required": {
                "model": ("MODEL",), "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "lora_1_name": (lst, ), "lora_1_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_1_mode": (modes, {"default": "All"}), "lora_1_config": ("STRING", {"default": "1"}),
                "lora_2_name": (lst, ), "lora_2_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_2_mode": (modes, {"default": "All"}), "lora_2_config": ("STRING", {"default": "1"}),
                "lora_3_name": (lst, ), "lora_3_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_3_mode": (modes, {"default": "All"}), "lora_3_config": ("STRING", {"default": "1"}),
            },
            "optional": { "optional_model_stack": ("MODEL",), "optional_clip_stack": ("CLIP",), }
        }

# ==============================================================================
#  VARIANT 3: SDXL ONLY
# ==============================================================================
class LevelX_SDXLAutoLoRA(LevelX_BaseAutoLoRA):
    @classmethod
    def INPUT_TYPES(s):
        lst = get_filtered_loras("SDXL")
        modes = ["All", "First", "By Index", "Custom Override", "None"]
        return {
            "required": {
                "model": ("MODEL",), "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "lora_1_name": (lst, ), "lora_1_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_1_mode": (modes, {"default": "All"}), "lora_1_config": ("STRING", {"default": "1"}),
                "lora_2_name": (lst, ), "lora_2_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_2_mode": (modes, {"default": "All"}), "lora_2_config": ("STRING", {"default": "1"}),
                "lora_3_name": (lst, ), "lora_3_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_3_mode": (modes, {"default": "All"}), "lora_3_config": ("STRING", {"default": "1"}),
            },
            "optional": { "optional_model_stack": ("MODEL",), "optional_clip_stack": ("CLIP",), }
        }
# ==============================================================================
#  VARIANT 4: FLUX 2 ONLY
# ==============================================================================
class LevelX_Flux2AutoLoRA(LevelX_BaseAutoLoRA):
    @classmethod
    def INPUT_TYPES(s):
        lst = get_filtered_loras("FLUX2")
        modes = ["All", "First", "By Index", "Custom Override", "None"]
        return {
            "required": {
                "model": ("MODEL",), "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "lora_1_name": (lst, ), "lora_1_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_1_mode": (modes, {"default": "All"}), "lora_1_config": ("STRING", {"default": "1"}),
                "lora_2_name": (lst, ), "lora_2_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_2_mode": (modes, {"default": "All"}), "lora_2_config": ("STRING", {"default": "1"}),
                "lora_3_name": (lst, ), "lora_3_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_3_mode": (modes, {"default": "All"}), "lora_3_config": ("STRING", {"default": "1"}),
            },
            "optional": { "optional_model_stack": ("MODEL",), "optional_clip_stack": ("CLIP",), }
        }

# ==============================================================================
#  VARIANT 5: QWEN ONLY
# ==============================================================================
class LevelX_QwenAutoLoRA(LevelX_BaseAutoLoRA):
    @classmethod
    def INPUT_TYPES(s):
        lst = get_filtered_loras("Qwen")
        modes = ["All", "First", "By Index", "Custom Override", "None"]
        return {
            "required": {
                "model": ("MODEL",), "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "lora_1_name": (lst, ), "lora_1_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_1_mode": (modes, {"default": "All"}), "lora_1_config": ("STRING", {"default": "1"}),
                "lora_2_name": (lst, ), "lora_2_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_2_mode": (modes, {"default": "All"}), "lora_2_config": ("STRING", {"default": "1"}),
                "lora_3_name": (lst, ), "lora_3_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_3_mode": (modes, {"default": "All"}), "lora_3_config": ("STRING", {"default": "1"}),
            },
            "optional": { "optional_model_stack": ("MODEL",), "optional_clip_stack": ("CLIP",), }
        }

# ==============================================================================
#  VARIANT 6: Z-IMAGE ONLY
# ==============================================================================
class LevelX_ZImageAutoLoRA(LevelX_BaseAutoLoRA):
    @classmethod
    def INPUT_TYPES(s):
        lst = get_filtered_loras("Zimage")
        modes = ["All", "First", "By Index", "Custom Override", "None"]
        return {
            "required": {
                "model": ("MODEL",), "clip": ("CLIP",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "lora_1_name": (lst, ), "lora_1_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_1_mode": (modes, {"default": "All"}), "lora_1_config": ("STRING", {"default": "1"}),
                "lora_2_name": (lst, ), "lora_2_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_2_mode": (modes, {"default": "All"}), "lora_2_config": ("STRING", {"default": "1"}),
                "lora_3_name": (lst, ), "lora_3_strength": ("FLOAT", {"default": 1.0, "step": 0.01}),
                "lora_3_mode": (modes, {"default": "All"}), "lora_3_config": ("STRING", {"default": "1"}),
            },
            "optional": { "optional_model_stack": ("MODEL",), "optional_clip_stack": ("CLIP",), }
        }

# ==============================================================================
#  NODE 7: TRIGGER MANAGER
# ==============================================================================
class LevelX_TriggerSaver:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "operation": (["Read Entry", "Overwrite Entry", "Append to Entry", "Remove Word", "SCAN LOCAL (Fast)", "SCAN ONLINE (Slow/Deep)"],),
                "lora_name": (folder_paths.get_filename_list("loras"), ),
                "trigger_word": ("STRING", {"multiline": False, "default": ""}),
            }
        }
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status_report", "current_triggers")
    FUNCTION = "manage_triggers"
    CATEGORY = "Level X/Utils"
    OUTPUT_NODE = True

    def scan_civitai_info(self, base_path):
        info_path = base_path + ".civitai.info"
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "trainedWords" in data and data["trainedWords"]:
                        return ", ".join(data["trainedWords"])
            except: pass
        return None

    def scan_txt_sidecar(self, base_path):
        txt_path = base_path + ".txt"
        if os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if len(content) < 200: return content
            except: pass
        return None

    def scan_safetensors_meta(self, file_path):
        try:
            with safe_open(file_path, framework="pt", device="cpu") as f:
                meta = f.metadata()
                if not meta: return None
                if "modelspec.trigger_phrase" in meta: return meta["modelspec.trigger_phrase"]
                if "ss_tag_frequency" in meta:
                    tags_json = json.loads(meta["ss_tag_frequency"])
                    all_tags = []
                    for ds, tags in tags_json.items():
                        sorted_tags = sorted(tags.items(), key=lambda item: item[1], reverse=True)
                        if sorted_tags: all_tags.append(sorted_tags[0][0])
                    if all_tags: return ", ".join(list(set(all_tags)))
        except: pass
        return None

    def scan_online_civitai(self, filename):
        try:
            query = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
            encoded = urllib.parse.quote(query)
            url = f"https://civitai.com/api/v1/models?query={encoded}&limit=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read().decode())
                if "items" in data and len(data["items"]) > 0:
                    model = data["items"][0]
                    for version in model.get("modelVersions", []):
                        if version.get("trainedWords"): return ", ".join(version["trainedWords"])
        except Exception as e: print(f"[Level X] Online Search Failed for {filename}: {e}")
        return None

    def manage_triggers(self, operation, lora_name, trigger_word):
        db = load_db()
        clean_name = lora_name.replace("\\", "/").strip()
        existing_triggers = db.get(clean_name, "")
        
        if operation == "Read Entry": return (f"Read Mode: {clean_name}", existing_triggers)
        elif operation == "Overwrite Entry":
            db[clean_name] = trigger_word
            save_db(db)
            return (f"Overwrote: {clean_name}", db[clean_name])
        elif operation == "Append to Entry":
            if existing_triggers:
                if trigger_word.lower() not in existing_triggers.lower(): db[clean_name] = f"{existing_triggers}, {trigger_word}"
            else: db[clean_name] = trigger_word
            save_db(db)
            return (f"Appended: {clean_name}", db[clean_name])
        elif operation == "Remove Word":
            if existing_triggers:
                trigs = [t.strip() for t in existing_triggers.split(",") if t.strip()]
                trigs = [t for t in trigs if t.lower() != trigger_word.strip().lower()]
                db[clean_name] = ", ".join(trigs)
                save_db(db)
            return (f"Removed word from: {clean_name}", db.get(clean_name, ""))

        is_online = (operation == "SCAN ONLINE (Slow/Deep)")
        lora_root = folder_paths.get_folder_paths("loras")[0]
        count_new, count_checked = 0, 0
        print(f"[Level X] 🚀 Starting Scan (Online: {is_online})...")

        for root, dirs, files in os.walk(lora_root):
            for file in files:
                if file.endswith(".safetensors") or file.endswith(".ckpt"):
                    count_checked += 1
                    full_path = os.path.join(root, file)
                    base_path = os.path.splitext(full_path)[0]
                    rel_path = os.path.relpath(full_path, lora_root).replace("\\", "/")
                    
                    if rel_path not in db or not db[rel_path]:
                        found = None
                        if not found: found = self.scan_civitai_info(base_path)
                        if not found: found = self.scan_safetensors_meta(full_path)
                        if not found: found = self.scan_txt_sidecar(base_path)
                        if not found and is_online:
                            print(f"   -> ☁️ Searching online for: {file}")
                            found = self.scan_online_civitai(file)

                        if found:
                            db[rel_path] = found
                            count_new += 1
                            print(f"   -> ✅ Found: {rel_path} = {found}")

        if count_new > 0:
            save_db(db)
            msg = f"Scan Complete: Added {count_new} triggers [Online: {is_online}]"
        else: msg = f"Scan Complete: No new triggers found. (Checked {count_checked})"
        return (msg, "")