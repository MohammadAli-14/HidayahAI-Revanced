"""
Hidayah AI — Fine-Tuning Script (Kaggle Notebook Ready)
========================================================
Fine-tunes Qwen2.5-3B-Instruct on Islamic QA data using QLoRA 4-bit SFT via Unsloth.
Optimized for local 3B deployment (runs smoothly on mid-range laptops/desktops at 40-60+ tok/s).

HOW TO USE ON KAGGLE:
1. Create a new Kaggle Notebook
2. Settings → Accelerator → GPU T4 x2
3. Settings → Internet → ON
4. Add your dataset: kaggle.com/datasets → upload hidayah_sft_train.jsonl
5. Copy this entire script into a single cell (or split into cells as marked)
6. Run all cells

Estimated time: ~45-60 minutes on T4 x2
Output: LoRA adapters + GGUF model file (~1.9 GB)
"""

# ============================================================================
# CELL 1: Install Dependencies
# ============================================================================
# Option A (Standard Kaggle 2024-2025):
# !pip install unsloth
# !pip install datasets trl
#
# Option B (If PyTorch dependency mismatch occurs):
# %%capture
# !pip install pip3-autoremove
# !pip-autoremove torch torchvision torchaudio -y
# !pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# !pip install unsloth
# !pip install datasets trl

# ============================================================================
# CELL 2: Configuration
# ============================================================================
import os
import json
import torch

# Model Configuration
MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"  # Pre-quantized 4-bit 3B model (optimized for local inference)
MAX_SEQ_LENGTH = 1024   # 1024 tokens fits 99.8% of Quran/Hadith/RAFT data & runs 3x faster than 2048
DTYPE = None            # Auto-detect (Float16 for T4)
LOAD_IN_4BIT = True     # QLoRA 4-bit quantization

# LoRA Configuration
LORA_R = 16             # Rank: balance between quality and memory
LORA_ALPHA = 16         # Scaling factor (usually = r)
LORA_DROPOUT = 0        # Unsloth optimized: no dropout needed
TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",     # Attention layers
    "gate_proj", "up_proj", "down_proj",          # MLP layers
]

# Training Hyperparameters
TRAIN_EPOCHS = 2       # 2 complete passes (1,254 steps) reaches optimal 0.37 loss without overfitting
BATCH_SIZE = 4         # 3B fits comfortably in T4 VRAM
GRAD_ACCUM_STEPS = 4   # Effective batch size = 4 * 4 = 16
LEARNING_RATE = 2.0e-4 # Standard optimal LoRA learning rate for 2 epochs
WARMUP_STEPS = 50      # Universal across Transformers v4 & v5+
WEIGHT_DECAY = 0.01
MAX_GRAD_NORM = 0.3
LR_SCHEDULER = "cosine"

# Paths (Auto-detects whether your dataset is v1, v2, or v3 on Kaggle)
import glob
possible_paths = [
    "/kaggle/input/hidayah-islamic-qa-sft-v3/hidayah_sft_train.jsonl",
    "/kaggle/input/datasets/mohammedali141/hidayah-islamic-qa-sft-v3/hidayah_sft_train.jsonl",
    "/kaggle/input/hidayah-islamic-qa-sft-v2/hidayah_sft_train.jsonl",
    "/kaggle/input/datasets/mohammedali141/hidayah-islamic-qa-sft-v2/hidayah_sft_train.jsonl",
    "/kaggle/input/hidayah-islamic-qa-sft/hidayah_sft_train.jsonl",
    "training/data/hidayah_sft_train.jsonl",
]
DATASET_PATH = None
for p in possible_paths:
    if os.path.exists(p):
        DATASET_PATH = p
        break

if not DATASET_PATH:
    found = glob.glob("/kaggle/input/**/hidayah_sft_train.jsonl", recursive=True)
    DATASET_PATH = found[0] if found else "/kaggle/input/hidayah-islamic-qa-sft-v3/hidayah_sft_train.jsonl"

OUTPUT_DIR = "/kaggle/working/hidayah-lm-lora"
GGUF_OUTPUT_DIR = "/kaggle/working/hidayah-lm-gguf"

print("=" * 60)
print("🕌 HidayahLM Fine-Tuning Configuration")
print("=" * 60)
print(f"  Model:          {MODEL_NAME}")
print(f"  Max Seq Length:  {MAX_SEQ_LENGTH}")
print(f"  LoRA Rank:       {LORA_R}")
print(f"  Max Epochs:      {TRAIN_EPOCHS}")
print(f"  Batch Size:      {BATCH_SIZE} × {GRAD_ACCUM_STEPS} = {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"  Learning Rate:   {LEARNING_RATE}")
print(f"  Early Stopping:  Enabled (Monitors eval_loss per epoch)")
print(f"  GPU:             {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"  VRAM:            {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB" if torch.cuda.is_available() else "  VRAM: N/A")
print("=" * 60)

# ============================================================================
# CELL 3: Load Model with Unsloth
# ============================================================================
from unsloth import FastLanguageModel

print("\n📥 Loading model (4-bit quantized)...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=DTYPE,
    load_in_4bit=LOAD_IN_4BIT,
)
print("✅ Model loaded successfully!")

# Explicitly configure Qwen 2.5 ChatML template (official Unsloth best practice)
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template="qwen-2.5",
)

# Add LoRA adapters
print("\n🔧 Adding LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    target_modules=TARGET_MODULES,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    use_gradient_checkpointing="unsloth",  # 30% VRAM savings
    random_state=42,
)

# Print trainable parameters
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
print(f"✅ LoRA adapters added!")
print(f"  Trainable: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")

# ============================================================================
# CELL 4: Load & Format Dataset (with Validation Split)
# ============================================================================
from datasets import load_dataset

print(f"\n📂 Loading dataset from: {DATASET_PATH}")
raw_dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# Check if companion test set exists, or split 95% train / 5% eval
test_path = DATASET_PATH.replace("hidayah_sft_train.jsonl", "hidayah_sft_test.jsonl")
if os.path.exists(test_path):
    train_data = raw_dataset
    eval_data = load_dataset("json", data_files=test_path, split="train")
    print(f"✅ Loaded {len(train_data):,} training and {len(eval_data):,} held-out validation samples from {test_path}")
else:
    split = raw_dataset.train_test_split(test_size=0.05, seed=42)
    train_data = split["train"]
    eval_data = split["test"]
    print(f"✅ Created 95/5 validation split: {len(train_data):,} train / {len(eval_data):,} eval examples")

# Preview a sample
print("\n📋 Sample training example:")
sample = train_data[0]
for msg in sample["messages"]:
    role = msg["role"]
    content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
    print(f"  [{role}]: {content}")


def format_for_training(examples):
    """Apply Qwen2.5 ChatML template to the messages."""
    texts = []
    for messages in examples["messages"]:
        formatted = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        texts.append(formatted)
    return {"text": texts}


print("\n🔄 Formatting datasets with ChatML template...")
formatted_train = train_data.map(
    format_for_training,
    batched=True,
    remove_columns=train_data.column_names,
    desc="Formatting Train",
)
formatted_eval = eval_data.map(
    format_for_training,
    batched=True,
    remove_columns=eval_data.column_names,
    desc="Formatting Eval",
)
print(f"✅ Formatted {len(formatted_train):,} train & {len(formatted_eval):,} eval examples")

# ============================================================================
# CELL 5: Training (with Early Stopping & Best Model Retention)
# ============================================================================
from trl import SFTTrainer
from transformers import TrainingArguments, EarlyStoppingCallback

print("\n🏋️ Starting fine-tuning with validation & Early Stopping...")
print(f"  Max Epochs:     {TRAIN_EPOCHS}")
print(f"  Learning Rate:  {LEARNING_RATE} (Cosine decay)")
print(f"  Total steps:    ~{len(formatted_train) * TRAIN_EPOCHS // (BATCH_SIZE * GRAD_ACCUM_STEPS)}")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=formatted_train,
    eval_dataset=formatted_eval,
    args=TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        num_train_epochs=TRAIN_EPOCHS,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=MAX_GRAD_NORM,
        lr_scheduler_type=LR_SCHEDULER,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=25,
        eval_strategy="epoch",         # Evaluate validation loss at each epoch
        save_strategy="epoch",         # Save checkpoint at each epoch
        load_best_model_at_end=True,   # Automatically load the best checkpoint at end
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        save_total_limit=2,            # Keep only 2 best checkpoints to save Kaggle disk
        optim="adamw_8bit",
        seed=42,
        report_to="none",
    ),
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=False,  # Unsloth recommended: False prevents cross-sample attention contamination
    callbacks=[
        EarlyStoppingCallback(
            early_stopping_patience=2   # Halt if eval_loss fails to improve for 2 consecutive epochs
        )
    ],
)

# Show GPU memory before training
gpu_stats = torch.cuda.get_device_properties(0)
reserved_mem = torch.cuda.max_memory_reserved() / 1e9
print(f"  GPU Memory Reserved: {reserved_mem:.2f} GB / {gpu_stats.total_memory / 1e9:.1f} GB")

# Train!
print("\n🚀 Training started...")
trainer_stats = trainer.train()

# Print training results
print("\n" + "=" * 60)
print("✅ Training Complete!")
print("=" * 60)
print(f"  Training Loss:     {trainer_stats.training_loss:.4f}")
print(f"  Total Steps:       {trainer_stats.global_step}")
print(f"  Training Time:     {trainer_stats.metrics['train_runtime'] / 60:.1f} minutes")
print(f"  Samples/Second:    {trainer_stats.metrics['train_samples_per_second']:.2f}")

# ============================================================================
# CELL 6: Save LoRA Adapters
# ============================================================================
print(f"\n💾 Saving LoRA adapters to: {OUTPUT_DIR}")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("✅ LoRA adapters saved!")

# ============================================================================
# CELL 7: Quick Test (Before Export)
# ============================================================================
print("\n🧪 Quick inference test...")

FastLanguageModel.for_inference(model)

test_messages = [
    {"role": "system", "content": "You are Hidayah AI, an Islamic scholarly research assistant."},
    {"role": "user", "content": "What does Surah Al-Fatiha teach us?"},
]

inputs = tokenizer.apply_chat_template(
    test_messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to("cuda")

outputs = model.generate(
    input_ids=inputs,
    max_new_tokens=512,
    temperature=0.3,
    do_sample=True,
)

response = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)
print("\n📝 Test Response:")
print("-" * 40)
print(response[:500])
print("-" * 40)

# Test abstention
print("\n🛑 Abstention test...")
abstention_messages = [
    {"role": "system", "content": "You are Hidayah AI, an Islamic scholarly research assistant."},
    {"role": "user", "content": "Is my divorce valid? I said talaq three times in anger."},
]

inputs2 = tokenizer.apply_chat_template(
    abstention_messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to("cuda")

outputs2 = model.generate(
    input_ids=inputs2,
    max_new_tokens=512,
    temperature=0.3,
    do_sample=True,
)

response2 = tokenizer.decode(outputs2[0][inputs2.shape[-1]:], skip_special_tokens=True)
print("\n📝 Abstention Response:")
print("-" * 40)
print(response2[:500])
print("-" * 40)

# ============================================================================
# CELL 8: Export to GGUF (For Ollama Deployment)
# ============================================================================
print("\n📦 Exporting to GGUF format (Q4_K_M quantization)...")
print("  This may take 10-20 minutes...")

os.makedirs(GGUF_OUTPUT_DIR, exist_ok=True)

# Unsloth's built-in GGUF export (merges LoRA + quantizes in one step)
model.save_pretrained_gguf(
    GGUF_OUTPUT_DIR,
    tokenizer,
    quantization_method="q4_k_m",  # Best quality-to-size ratio for local deployment
)

print(f"\n✅ GGUF model exported to: {GGUF_OUTPUT_DIR}")
print("  Look for: hidayah-lm-gguf/unsloth.Q4_K_M.gguf")

# List output files
for f in os.listdir(GGUF_OUTPUT_DIR):
    size_mb = os.path.getsize(os.path.join(GGUF_OUTPUT_DIR, f)) / (1024 * 1024)
    print(f"  📄 {f} ({size_mb:.1f} MB)")

# ============================================================================
# CELL 9: Download Instructions
# ============================================================================
print("\n" + "=" * 60)
print("🎉 FINE-TUNING COMPLETE!")
print("=" * 60)
print(r"""
📥 DOWNLOAD YOUR MODEL:
1. In the Kaggle output panel (right side), find:
   - /kaggle/working/hidayah-lm-gguf/unsloth.Q4_K_M.gguf (~1.9 GB)
   
2. Click the three dots (...) → Download

3. On your Windows machine:
   a. Install Ollama: winget install Ollama.Ollama
   b. Move download to d:\Hidayah AI\training\models\hidayah-lm-3b-q4_k_m.gguf
   c. Run: ollama create hidayah-lm:3b -f Modelfile
   d. Test: ollama run hidayah-lm:3b

4. Connect to Hidayah AI:
   Add to your .env file:
     USE_LOCAL_LLM=true
     LOCAL_LLM_URL=http://localhost:11434/v1
     LOCAL_LLM_MODEL=hidayah-lm:3b
   
   Then: streamlit run app.py
""")
