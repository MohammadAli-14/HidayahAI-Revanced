# 🕌 HidayahLM Fine-Tuning Guide

> Complete step-by-step guide to fine-tune Qwen2.5-7B-Instruct on Islamic QA data using Kaggle GPU and deploy via Ollama.

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Kaggle Account** | Free at [kaggle.com](https://kaggle.com) |
| **Kaggle GPU** | 30 hours/week free (T4 x2) |
| **Ollama** | Free at [ollama.com](https://ollama.com) |
| **Disk Space** | ~5 GB for the GGUF model file |
| **RAM** | 8+ GB recommended for local inference |

---

## Step-by-Step Instructions

### STEP 1: Prepare the Dataset (Local, ~5 minutes)

Open PowerShell in the project root and run:

```powershell
cd "d:\Hidayah AI"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run dataset preparation
python training/prepare_dataset.py
```

**Expected Output:**
```
🕌 Hidayah AI — Dataset Preparation for Fine-Tuning
📖 Step 1: Extracting Quran Q&A from LanceDB...
  ✅ 6,236 Quran examples
📜 Step 2: Extracting Hadith Q&A from LanceDB...
  ✅ 50,762 Hadith examples
🧠 Step 3: Creating synthetic training examples...
  ✅ 25 synthetic examples (abstention + madhhab + citation)
📊 Total examples: ~57,023
✅ Training set: ~54,173 examples → training/data/hidayah_sft_train.jsonl
✅ Test set:     ~500 examples → training/data/hidayah_sft_test.jsonl
```

**Output Files:**
- `training/data/hidayah_sft_train.jsonl` — Upload this to Kaggle
- `training/data/hidayah_sft_test.jsonl` — Keep for evaluation later

---

### STEP 2: Upload Dataset to Kaggle

1. Go to [kaggle.com/datasets/new](https://www.kaggle.com/datasets/new)
2. Click **"New Dataset"**
3. Upload `training/data/hidayah_sft_train.jsonl`
4. Name the dataset: `hidayah-islamic-qa-sft`
5. Set visibility to **Private** (or Public if you want)
6. Click **Create**

> ⚠️ Wait for the upload to complete before proceeding.

---

### STEP 3: Create Kaggle Notebook

1. Go to [kaggle.com/code](https://www.kaggle.com/code)
2. Click **"+ New Notebook"**
3. **Settings (right panel):**
   - **Accelerator:** GPU T4 x2
   - **Internet:** ON ✅
   - **Persistence:** Files (so you can download output)
4. **Add Input (right panel → Add Data):**
   - Search for your dataset: `hidayah-islamic-qa-sft`
   - Add it

---

### STEP 4: Run the Training Script

Copy the content of `training/train_hidayah_lm.py` into Kaggle cells.

**Recommended cell split:**

| Cell # | Section | What It Does | Time |
|--------|---------|-------------|------|
| 1 | Install Dependencies | Installs Unsloth, TRL, etc. | ~3 min |
| 2 | Configuration | Sets all hyperparameters | Instant |
| 3 | Load Model | Downloads Qwen2.5-7B 4-bit | ~5 min |
| 4 | Load Dataset | Loads & formats your JSONL | ~1 min |
| 5 | Training | Fine-tunes the model | **~2-3 hours** |
| 6 | Save Adapters | Saves LoRA weights | ~1 min |
| 7 | Quick Test | Tests inference quality | ~1 min |
| 8 | Export GGUF | Merges + quantizes to GGUF | ~15 min |
| 9 | Download Info | Shows download instructions | Instant |

**CELL 1 — Install Dependencies (IMPORTANT: Uncomment the install lines!):**
```python
%%capture
!pip install pip3-autoremove
!pip-autoremove torch torchvision torchaudio -y
!pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121
!pip install "unsloth[kaggle] @ git+https://github.com/unslothai/unsloth.git"
!pip install datasets trl
```

**CELL 2 onwards:** Copy from `training/train_hidayah_lm.py` starting from `# CELL 2: Configuration`

> ⚠️ **IMPORTANT:** In Cell 2, make sure `DATASET_PATH` matches your Kaggle dataset path:
> ```python
> DATASET_PATH = "/kaggle/input/hidayah-islamic-qa-sft/hidayah_sft_train.jsonl"
> ```

---

### STEP 5: Download the GGUF Model

After training completes:

1. In the **Output** panel (right side of Kaggle), navigate to:
   ```
   /kaggle/working/hidayah-lm-gguf/
   ```
2. Find `unsloth.Q4_K_M.gguf` (~4.5 GB)
3. Click the **three dots (⋯)** → **Download**
4. Save to: `d:\Hidayah AI\training\models\`

> 💡 **Alternative:** If download is slow, you can also push the model to HuggingFace Hub directly from the notebook:
> ```python
> model.push_to_hub_gguf("YOUR_USERNAME/hidayah-lm-7b", tokenizer, quantization_method="q4_k_m")
> ```

---

### STEP 6: Install Ollama & Deploy Locally

#### 6a. Install Ollama

```powershell
# Option 1: Using winget
winget install Ollama.Ollama

# Option 2: Download from https://ollama.com/download
```

After installation, Ollama runs as a background service automatically.

#### 6b. Create and Import Your Model

```powershell
# Navigate to where you saved the GGUF file
cd "d:\Hidayah AI\training\models"

# Copy the Modelfile
copy "..\Modelfile" .

# Rename the GGUF file to match what the Modelfile expects
ren "unsloth.Q4_K_M.gguf" "hidayah-lm-q4_k_m.gguf"

# Create the Ollama model
ollama create hidayah-lm:7b -f Modelfile
```

#### 6c. Test Your Model

```powershell
# Interactive chat
ollama run hidayah-lm:7b

# Test specific queries
ollama run hidayah-lm:7b "What does Surah Al-Fatiha teach us?"
ollama run hidayah-lm:7b "Is my divorce valid?"
```

#### 6d. Verify API Endpoint

```powershell
# Test the OpenAI-compatible API (this is what Hidayah AI uses)
curl http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model":"hidayah-lm:7b","messages":[{"role":"user","content":"What is Surah Al-Ikhlas about?"}]}'
```

---

### STEP 7: Connect to Hidayah AI

#### 7a. Update `.env`

Add these lines to `d:\Hidayah AI\.env`:

```ini
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=hidayah-lm:7b
```

#### 7b. Run the App

```powershell
cd "d:\Hidayah AI"
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

#### 7c. Test in Browser

Open `http://localhost:8501` and ask:

| Test Query | Expected Behavior |
|---|---|
| "What does Surah An-Nisa verse 11 state about inheritance?" | Multi-Madhhab scholarly response with [Q#] citations |
| "Is my divorce valid?" | ⚠️ Personal Fatwa Boundary Notice (abstention) |
| "What are the pillars of prayer?" | Academic response with all 4 Madhhab views |
| "هل طلاقي صحيح؟" | Arabic abstention response |

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|---|---|
| **Kaggle OOM (Out of Memory)** | Reduce `MAX_SEQ_LENGTH` to 1024 or `LORA_R` to 8 |
| **Kaggle "No GPU available"** | Wait and try again, or use T4 x1 |
| **Ollama "model not found"** | Run `ollama list` to check model name |
| **Ollama slow responses** | Normal for 7B model on CPU; ~10-30 sec per response |
| **Hidayah AI not using local LLM** | Check `.env` has `USE_LOCAL_LLM=true` (no quotes!) |
| **Arabic text garbled** | Add `sys.stdout.reconfigure(encoding='utf-8')` |

### Verifying Ollama is Running

```powershell
# Check if Ollama service is running
ollama list

# If not, start it
ollama serve
```

---

## File Structure

```
training/
├── prepare_dataset.py          # Step 1: Creates training data from LanceDB
├── train_hidayah_lm.py         # Step 4: Kaggle training script
├── Modelfile                   # Step 6: Ollama deployment config
├── requirements_training.txt   # Training-only dependencies
├── README.md                   # This file
├── data/                       # Created by prepare_dataset.py
│   ├── hidayah_sft_train.jsonl # Training set (~55K examples)
│   └── hidayah_sft_test.jsonl  # Test set (~500 examples)
└── models/                     # Created by you after Kaggle download
    └── hidayah-lm-q4_k_m.gguf # The fine-tuned GGUF model (~4.5 GB)
```

---

## What Makes This Unique (For Publication)

1. **First open-source Fatwa-Aligned SFT** — Model trained with abstention-aware examples
2. **Multi-Madhhab balanced** — Presents all 4 Sunni schools neutrally
3. **Defense-in-depth** — Both code-level guardrails AND model-level abstention training
4. **RAG + Fine-tuned LLM** — Canonical corpus (LanceDB) + specialized model
5. **End-to-end pipeline** — Dataset → Training → Quantization → Deployment → App integration
6. **Trilingual** — English, Arabic, Urdu support
