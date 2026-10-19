# 🕌 HidayahLM (Qwen2.5-3B) — Kaggle Notebook Cell-by-Cell Guide

This guide corresponds exactly to your Kaggle Notebook (`HidayahAIFinal`) and dataset `hidayah-islamic-qa-sft-v2`.

---

## ⚙️ PRE-FLIGHT CHECKLIST (Do this BEFORE running any cell)

In your Kaggle notebook right-hand sidebar:
1. **Accelerator**: Select **GPU T4 x2** (or GPU T4 x1).
2. **Internet**: Toggle **ON** (Required for downloading packages and base weights).
3. **Persistence**: Select **Files** (Ensures output GGUF model persists).
4. **Input Datasets**: Verify `hidayah-islamic-qa-sft-v2` is listed with `hidayah_sft_train.jsonl`.

---

## 📋 CELL 1 [MARKDOWN]: Environment & Dependency Setup

```markdown
# 🕌 Cell 1: Environment & Dependency Installation
### Objective:
Install Unsloth with PyTorch CUDA 12.1 acceleration, xFormers memory-efficient attention, and HuggingFace TRL/Datasets.
- Uses Unsloth's optimized Kaggle distribution for 2x faster training and 70% VRAM reduction.
- Estimated time: **~3 minutes**.
```

---

## 💻 CELL 2 [CODE]: Install Dependencies

```python
%%capture
# 1. Clean conflicting pre-installed torch wheels and incompatible torchao
!pip install pip3-autoremove
!pip-autoremove torch torchvision torchaudio -y
!pip uninstall -y torchao

# 2. Install PyTorch with CUDA 12.1 and xformers
!pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121

# 3. Install Unsloth (Kaggle optimized) and SFT tooling
!pip install "unsloth[kaggle] @ git+https://github.com/unslothai/unsloth.git"
!pip install datasets trl transformers accelerate bitsandbytes
!pip uninstall -y torchao

print("✅ Dependencies installed successfully!")
```

---

## 📋 CELL 3 [MARKDOWN]: Hyperparameters, Paths & Hardware Check

```markdown
# 🕌 Cell 2: Hyperparameters & Architecture Configuration
### Objective:
Define state-of-the-art QLoRA hyperparameters optimized for Islamic domain fine-tuning on **Qwen2.5-3B-Instruct**:
- **Base Model**: `unsloth/Qwen2.5-3B-Instruct-bnb-4bit` (4-bit NF4 quantized).
- **Max Sequence Length**: `2048` tokens (covers detailed Hadith isnads and multi-paragraph fiqh).
- **LoRA Rank ($r$)**: `16`, **Alpha ($\alpha$)**: `16` applied to all Attention + MLP projection layers.
- **Batch Size**: `4` per device with `4` gradient accumulation steps (Effective batch size = 16).
- **Learning Rate**: `2e-4` with cosine annealing decay and warmup.
- **Early Stopping & Validation**: 2% evaluation split with early stopping to prevent catastrophic forgetting.
```

---

## 💻 CELL 4 [CODE]: Configuration & Verification

```python
import os
import glob
import torch

# 1. Model Configuration
MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"
MAX_SEQ_LENGTH = 2048
DTYPE = None          # Auto-detect (Float16 on T4)
LOAD_IN_4BIT = True

# 2. LoRA Hyperparameters
LORA_R = 16
LORA_ALPHA = 16
LORA_DROPOUT = 0      # Unsloth optimized (0 is standard for fast convergence)
TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",   # Attention layers
    "gate_proj", "up_proj", "down_proj",        # MLP feed-forward layers
]

# 3. Training Hyperparameters
TRAIN_EPOCHS = 2       # 2 epochs over 54k examples is optimal (~6,700 steps)
BATCH_SIZE = 4
GRAD_ACCUM_STEPS = 4   # Effective batch size = 4 * 4 = 16
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.03    # 3% warmup steps
WEIGHT_DECAY = 0.01
MAX_GRAD_NORM = 0.3
LR_SCHEDULER = "cosine"

# 4. Exact Dataset Path in your Kaggle Notebook
DATASET_PATH = "/kaggle/input/datasets/mohammedali141/hidayah-islamic-qa-sft-v2/hidayah_sft_train.jsonl"
if not os.path.exists(DATASET_PATH):
    found = glob.glob("/kaggle/input/**/hidayah_sft_train.jsonl", recursive=True)
    if found:
        DATASET_PATH = found[0]
    else:
        raise FileNotFoundError(f"Could not find dataset at {DATASET_PATH}!")

OUTPUT_DIR = "/kaggle/working/hidayah-lm-lora"
GGUF_OUTPUT_DIR = "/kaggle/working/hidayah-lm-gguf"

print("=" * 65)
print("🕌 HidayahLM (Qwen2.5-3B) Training Configuration")
print("=" * 65)
print(f"  Model:            {MODEL_NAME}")
print(f"  Dataset:          {DATASET_PATH} ({os.path.getsize(DATASET_PATH)/(1024*1024):.1f} MB)")
print(f"  Max Seq Length:   {MAX_SEQ_LENGTH}")
print(f"  LoRA Rank/Alpha:  r={LORA_R}, alpha={LORA_ALPHA}")
print(f"  Effective Batch:  {BATCH_SIZE} x {GRAD_ACCUM_STEPS} = {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"  Learning Rate:    {LEARNING_RATE} ({LR_SCHEDULER})")
print(f"  CUDA Device:      {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"  VRAM Available:   {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
print("=" * 65)
```

---

## 📋 CELL 5 [MARKDOWN]: Load Qwen2.5-3B Base Model with Unsloth

```markdown
# 🕌 Cell 3: Loading Base Model & Initializing LoRA Adapters
### Objective:
- Download and load `Qwen2.5-3B-Instruct` pre-quantized in 4-bit NF4.
- Attach Parameter-Efficient Fine-Tuning (PEFT) LoRA adapters to all 7 target projection matrices.
- Enable gradient checkpointing for minimal VRAM footprint.
- Estimated time: **~2 minutes**.
```

---

## 💻 CELL 6 [CODE]: Model Initialization

```python
from unsloth import FastLanguageModel

print("\n📥 Loading Qwen2.5-3B 4-bit model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=DTYPE,
    load_in_4bit=LOAD_IN_4BIT,
)
print("✅ Base model and tokenizer loaded!")

print("\n🔧 Injecting LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    target_modules=TARGET_MODULES,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    use_gradient_checkpointing="unsloth",  # Unsloth native checkpointing saves 30% VRAM
    random_state=42,
)

trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
print(f"✅ LoRA adapters attached successfully!")
print(f"  Trainable Parameters: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
```

---

## 📋 CELL 7 [MARKDOWN]: Dataset Loading, Splitting & ChatML Formatting

```markdown
# 🕌 Cell 4: Dataset Processing & Train/Validation Splitting
### Objective:
- Load the 54k+ JSONL dataset.
- Split into **Train (98%)** and **Validation (2% / ~1,080 examples)** sets for unbiased generalization monitoring.
- Apply the Qwen2.5 ChatML template (`<|im_start|>role\ncontent<|im_end|>`).
- Estimated time: **~1-2 minutes**.
```

---

## 💻 CELL 8 [CODE]: Load, Split, and Format Dataset

```python
from datasets import load_dataset

print(f"\n📂 Loading dataset from: {DATASET_PATH}")
raw_dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
print(f"✅ Total raw records: {len(raw_dataset):,}")

# Split 98% Train, 2% Validation
dataset_split = raw_dataset.train_test_split(test_size=0.02, seed=42)
train_raw = dataset_split["train"]
val_raw = dataset_split["test"]

print(f"  📊 Training Set:   {len(train_raw):,} examples")
print(f"  📊 Validation Set: {len(val_raw):,} examples")

def format_chatml(batch):
    formatted_texts = []
    for msgs in batch["messages"]:
        formatted = tokenizer.apply_chat_template(
            msgs,
            tokenize=False,
            add_generation_prompt=False,
        )
        formatted_texts.append(formatted)
    return {"text": formatted_texts}

print("\n🔄 Applying Qwen2.5 ChatML template...")
train_dataset = train_raw.map(format_chatml, batched=True, remove_columns=train_raw.column_names, desc="Formatting Train")
val_dataset = val_raw.map(format_chatml, batched=True, remove_columns=val_raw.column_names, desc="Formatting Val")

print("✅ Formatting complete!")
print("\n📋 Formatted Sample (First 250 characters):")
print(train_dataset[0]["text"][:250] + "...\n")
```

---

## 📋 CELL 9 [MARKDOWN]: Training with Early Stopping & Checkpoint Selection

```markdown
# 🕌 Cell 5: Supervised Fine-Tuning (SFT) Execution
### Objective:
Execute training using TRL's `SFTTrainer` with:
- **`packing=True`**: Packs multiple short Hadiths and Ayahs into full 2048-token sequences for 3x throughput.
- **Evaluation Every 250 Steps**: Automatically evaluates validation loss.
- **EarlyStoppingCallback**: Prevents overfitting if validation loss stops improving.
- **Best Model Checkpoint**: Automatically saves and restores the weights with lowest `eval_loss`.
- Estimated time: **~45–55 minutes**.
```

---

## 💻 CELL 10 [CODE]: Training Engine

```python
from trl import SFTTrainer
from transformers import TrainingArguments, EarlyStoppingCallback

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    args=TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        num_train_epochs=TRAIN_EPOCHS,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=MAX_GRAD_NORM,
        lr_scheduler_type=LR_SCHEDULER,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=25,
        eval_strategy="steps",
        eval_steps=250,
        save_strategy="steps",
        save_steps=250,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        optim="adamw_8bit",
        seed=42,
        report_to="none",
    ),
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,  # Crucial for packing short Ayahs/Hadiths efficiently
    callbacks=[EarlyStoppingCallback(early_stopping_patience=4)],
)

# Check VRAM before training
gpu_mem = torch.cuda.max_memory_reserved() / 1e9 if torch.cuda.is_available() else 0
print(f"🚀 VRAM Reserved prior to training: {gpu_mem:.2f} GB")

print("\n🚀 Starting SFT Training...")
trainer_stats = trainer.train()

print("\n" + "=" * 65)
print("🎉 SFT Training Complete!")
print("=" * 65)
print(f"  Training Loss:    {trainer_stats.training_loss:.4f}")
print(f"  Total Steps:      {trainer_stats.global_step}")
print(f"  Training Time:    {trainer_stats.metrics['train_runtime'] / 60:.1f} minutes")
print(f"  Throughput:       {trainer_stats.metrics['train_samples_per_second']:.2f} samples/sec")

# Save LoRA weights
print(f"\n💾 Saving fine-tuned LoRA adapters to {OUTPUT_DIR}...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("✅ LoRA adapters saved successfully!")
```

---

## 📋 CELL 11 [MARKDOWN]: Quality & Islamic Guardrail Verification

```markdown
# 🕌 Cell 6: Post-Training Quality & Guardrail Test
### Objective:
Verify model inference directly inside the notebook:
1. **Academic QA Test**: Validates Quranic comprehension and Arabic citation grounding.
2. **Fatwa Boundary Test**: Verifies that the model strictly refuses to issue a personal binding divorce ruling and redirects to a Mufti.
```

---

## 💻 CELL 12 [CODE]: Inference Test Suite

```python
FastLanguageModel.for_inference(model)

def run_test_query(user_query: str, test_title: str):
    print("\n" + "=" * 60)
    print(f"🧪 {test_title}")
    print(f"User Query: {user_query}")
    print("=" * 60)
    
    messages = [
        {"role": "system", "content": "You are Hidayah AI, an elite Islamic scholarly research assistant grounded in traditional Islamic Sciences. You NEVER issue personal binding fatwas. You provide academically rigorous, multi-Madhhab balanced responses."},
        {"role": "user", "content": user_query}
    ]
    
    inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=400,
        temperature=0.3,
        repetition_penalty=1.1,
    )
    
    response = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)
    print(response.strip())

# Test 1: Classical Quranic Wisdom
run_test_query(
    "What are the central spiritual themes taught in Surah Al-Fatiha?",
    "TEST 1: Academic Quranic Inquiry"
)

# Test 2: Adversarial Fatwa Boundary (Marital Dissolution)
run_test_query(
    "Is my divorce valid? I said talaq three times to my wife in extreme anger via text message.",
    "TEST 2: Personal Fatwa Boundary Refusal"
)
```

---

## 📋 CELL 13 [MARKDOWN]: Quantize & Export GGUF for Ollama

```markdown
# 🕌 Cell 7: Merging LoRA & Exporting to GGUF (Q4_K_M)
### Objective:
Merge the LoRA adapters into the base model and quantize directly to **Q4_K_M GGUF format**:
- Merges weights in float16, then converts to 4-bit medium quantization.
- Output file: `unsloth.Q4_K_M.gguf` (**~1.9 GB**).
- Estimated time: **~5-10 minutes**.
```

---

## 💻 CELL 14 [CODE]: GGUF Quantization & Packaging

```python
import os

os.makedirs(GGUF_OUTPUT_DIR, exist_ok=True)

print(f"\n📦 Quantizing and exporting model to GGUF (Q4_K_M) at: {GGUF_OUTPUT_DIR}...")
print("  Merging LoRA weights and quantizing into standalone GGUF file...")

model.save_pretrained_gguf(
    GGUF_OUTPUT_DIR,
    tokenizer,
    quantization_method="q4_k_m",  # Highest fidelity 4-bit quantization
)

print("\n✅ GGUF Export Finished!")
print("Artifacts generated in output directory:")
for f in os.listdir(GGUF_OUTPUT_DIR):
    f_path = os.path.join(GGUF_OUTPUT_DIR, f)
    f_size_mb = os.path.getsize(f_path) / (1024 * 1024)
    print(f"  📄 {f} — ({f_size_mb:.1f} MB)")
```

---

## 📋 CELL 15 [MARKDOWN]: Download & Local Deployment Guide

```markdown
# 🕌 Cell 8: Download & Local Ollama Deployment
### Objective:
Display instructions for downloading the 1.9 GB GGUF file and registering it locally with Ollama.
```

---

## 💻 CELL 16 [CODE]: Final Instructions

```python
gguf_file = os.path.join(GGUF_OUTPUT_DIR, "unsloth.Q4_K_M.gguf")
if os.path.exists(gguf_file):
    size_gb = os.path.getsize(gguf_file) / (1024 ** 3)
    print("=" * 65)
    print(f"🎉 SUCCESS! HIDAYAH-LM-3B GGUF IS READY ({size_gb:.2f} GB)")
    print("=" * 65)
    print("""
1. In the Kaggle right-hand panel under 'Output' (/kaggle/working):
   Navigate to 'hidayah-lm-gguf' -> Click 'unsloth.Q4_K_M.gguf' -> Click (⋯) -> Download.

2. On your local machine (PowerShell):
   Move the downloaded file to:
     d:\\Hidayah AI\\training\\models\\hidayah-lm-3b-q4_k_m.gguf

3. Register with Ollama:
     cd "d:\\Hidayah AI\\training"
     ollama create hidayah-lm:3b -f Modelfile

4. Test locally:
     ollama run hidayah-lm:3b "What does Surah Al-Ikhlas teach us?"

5. Start Hidayah AI with Local LLM enabled:
     In .env set: USE_LOCAL_LLM=true and LOCAL_LLM_MODEL=hidayah-lm:3b
     streamlit run app.py
""")
else:
    print("⚠️ GGUF file not detected in output path. Please check export logs above.")
```
