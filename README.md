# 🔥 ComfyUI-LevelX-Nodes

**The Ultimate "Fire & Forget" LoRA System for ComfyUI.** Automatically manages LoRA loading, trigger word injection, and database synchronization across multiple generation engines (SDXL, FLUX, Qwen, Z-Image).

---

## ✨ Key Features

### 1. 🧠 Intelligent Auto-Loader
Stop copy-pasting trigger words manually. These nodes automatically:
* **Load the LoRA Model:** Handles model & clip strength.
* **Inject Trigger Words:**
    * **Prefix Mode:** The 1st LoRA's trigger is forced to the *front* of your prompt (critical for style/character).
    * **Suffix Mode:** 2nd and 3rd LoRA triggers are appended to the *end*.
* **Smart Deduplication:** If you already typed the trigger, it won't add it again.
* **Engine Filtering:** Dedicated nodes for **SDXL**, **FLUX**, **FLUX 2**, **Qwen**, and **Z-Image** so you never load the wrong format.

### 2. 🕵️‍♂️ Advanced Trigger Manager
A powerful new node (`Level X Trigger Manager`) that builds your database for you.
* **Scan Local:** Instantaneously extracts triggers from:
    * `.civitai.info` files.
    * `.txt` sidecar files.
    * Internal `.safetensors` metadata (ModelSpec & Kohya).
* **Scan Online:** Queries the Civitai API live to find triggers for unknown LoRAs.
* **Force Re-Scan:** One-click option to rebuild your entire database from scratch.

### 3. 📂 Self-Healing Database
* **Location:** Stores data in `lora_trigger.json` right next to the nodes.
* **Auto-Update:** If a loader finds a new trigger during generation (via metadata), it silently updates the JSON file so the next run is instant.
* **Smart Caching:** Only reloads the JSON from disk if the file has actually changed, ensuring maximum performance.

---

## 🛠️ Installation

1.  **Navigate** to your custom nodes directory:
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  **Clone** or **Copy** the `ComfyUI-LevelX-Nodes` folder here.
3.  **Install Dependencies** (if missing):
    ```bash
    pip install safetensors
    ```
4.  **Restart ComfyUI**.

---

## 🚀 How to Use

### A. The Auto-Loaders (Generation)
1.  **Add Node:** Right-click > `Level X` > `Loaders`.
2.  **Select Engine:**
    * `🔥 Universal`: Shows ALL LoRAs (good for testing).
    * `⚡ FLUX`: Shows only `/FLUX` folder LoRAs.
    * `🎨 SDXL`: Shows only `/SDXL` folder LoRAs.
    * (Also available: `FLUX 2`, `Qwen`, `Z-Image`).
3.  **Connect:**
    * **Input:** Model & CLIP from your checkpoint.
    * **Prompt:** Connect your text prompt (Primitive/String).
    * **Output:** Connect Model/CLIP to KSampler, and `final_prompt` to your CLIP Text Encode.

**Visual Flow:**
[Checkpoint] ==(Model/CLIP)==> [🔥 Level X Auto-LoRA] ==(Model/CLIP)==> [KSampler]
[Prompt String] =============> [       Node       ] ==(final_prompt)==> [CLIP Text Encode]


### B. The Manager (Database Building)
1.  **Add Node:** Right-click > `Level X` > `Utils` > `Trigger Manager`.
2.  **Select Operation:**
    * `SCAN LOCAL (Fast)`: Quick update from local files.
    * `SCAN ONLINE (Slow)`: Deep search Civitai for missing tags.
    * `FORCE RE-SCAN`: Wipe and rebuild everything.
3.  **Run:** Queue the prompt (no inputs needed). Check the output string or console for the report:
    > "Scan Complete: Added 45 new triggers [Online: True]"

---

## ⚙️ Technical Details

### Database Logic
The system uses `lora_trigger.json` as the source of truth.
* **Format:** `{"SDXL/style.safetensors": "trigger_word, style"}`.
* **Matching:** Uses fuzzy matching (ignores case, spaces vs underscores).
* **Sync:** The manager node writes to this file. The loaders read from it.

### Folder Structure
To use the filtered nodes effectively, organize your `ComfyUI/models/loras/` directory like this:
models/loras/
├── SDXL/
│   └── character_a.safetensors
├── FLUX/
│   └── style_b.safetensors
├── FLUX2/
│   └── ...
└── Qwen/
└── ...

*(If you dump everything in root, just use the `🔥 Universal` node).*

## 🧪 Developer checks

If you want to run quick local checks before restarting ComfyUI:

- **Syntax-only compile (no runtime imports):**
    ```bash
    python -m py_compile lx_lora_node/lx_lora_node.py
    ```
    This checks for Python syntax errors without importing `comfy` or other runtime-only modules.

- **Dependencies:**
    ```bash
    pip install safetensors
    ```

- **DB location:** the active code stores the triggers JSON at `lx_lora_node/lora_trigger.json` (the package file). Both node files were updated to use this consolidated path.

- **Notes:** runtime errors may still occur inside ComfyUI if `comfy`, `folder_paths`, or network access are unavailable; check ComfyUI logs for those.
