"""
Hidayah AI — Fine-Tuning Script (Kaggle Notebook Ready)
========================================================
Fine-tunes Qwen2.5-7B-Instruct on Islamic QA data using QLoRA 4-bit SFT via Unsloth.

HOW TO USE ON KAGGLE:
1. Create a new Kaggle Notebook
2. Settings → Accelerator → GPU T4 x2
3. Settings → Internet → ON
4. Add your dataset: kaggle.com/datasets → upload hidayah_sft_train.jsonl
5. Copy this entire script into a single cell (or split into cells as marked)
6. Run all cells

Estimated time: 2-3 hours on T4 x2
Output: LoRA adapters + GGUF model file
"""

# ============================================================================
# CELL 1: Install Dependencies
# ============================================================================
# Uncomment the following lines when running on Kaggle:
# %%capture
# !pip install pip3-autoremove
# !pip-autoremove torch torchvision torchaudio -y
# !pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121
# !pip install "unsloth[kaggle] @ git+https://github.com/unslothai/unsloth.git"
# !pip install datasets trl

# ============================================================================
# CELL 2: Configuration
# ============================================================================
import os
import json
import torch

# Model Configuration
MODEL_NAME = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"  # Pre-quantized 4-bit model
MAX_SEQ_LENGTH = 2048   # Max context length (fits T4 16GB VRAM)
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
TRAIN_EPOCHS = 3
BATCH_SIZE = 2
GRAD_ACCUM_STEPS = 4    # Effective batch size = 2 * 4 = 8
LEARNING_RATE = 2e-4
WARMUP_STEPS = 10
WEIGHT_DECAY = 0.01
MAX_GRAD_NORM = 0.3
LR_SCHEDULER = "cosine"

# Paths (adjust for Kaggle)
# On Kaggle, your dataset will be at: /kaggle/input/hidayah-islamic-qa-sft/
DATASET_PATH = "/kaggle/input/hidayah-islamic-qa-sft/hidayah_sft_train.jsonl"
OUTPUT_DIR = "/kaggle/working/hidayah-lm-lora"
GGUF_OUTPUT_DIR = "/kaggle/working/hidayah-lm-gguf"

# For local testing, uncomment:
# DATASET_PATH = "training/data/hidayah_sft_train.jsonl"
# OUTPUT_DIR = "training/output/hidayah-lm-lora"
# GGUF_OUTPUT_DIR = "training/output/hidayah-lm-gguf"

print("=" * 60)
print("🕌 HidayahLM Fine-Tuning Configuration")
print("=" * 60)
print(f"  Model:          {MODEL_NAME}")
print(f"  Max Seq Length:  {MAX_SEQ_LENGTH}")
print(f"  LoRA Rank:       {LORA_R}")
print(f"  Epochs:          {TRAIN_EPOCHS}")
print(f"  Batch Size:      {BATCH_SIZE} × {GRAD_ACCUM_STEPS} = {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"  Learning Rate:   {LEARNING_RATE}")
print(f"  GPU:             {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"  VRAM:            {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB" if torch.cuda.is_available() else "  VRAM: N/A")
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
# CELL 4: Load & Format Dataset
# ============================================================================
from datasets import load_dataset

print(f"\n📂 Loading dataset from: {DATASET_PATH}")

# Load JSONL dataset
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
print(f"✅ Loaded {len(dataset)} training examples")

# Preview a sample
print("\n📋 Sample training example:")
sample = dataset[0]
for msg in sample["messages"]:
    role = msg["role"]
    content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
    print(f"  [{role}]: {content}")


def format_for_training(examples):
    """Apply Qwen2.5 ChatML template to the messages."""
    texts = []
    for messages in examples["messages"]:
        # Qwen2.5 uses ChatML format: <|im_start|>role\ncontent<|im_end|>
        formatted = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        texts.append(formatted)
    return {"text": texts}


print("\n🔄 Formatting dataset with ChatML template...")
formatted_dataset = dataset.map(
    format_for_training,
    batched=True,
    remove_columns=dataset.column_names,
    desc="Formatting",
)
print(f"✅ Formatted {len(formatted_dataset)} examples")

# Preview formatted output
print("\n📋 Formatted sample (first 300 chars):")
print(formatted_dataset[0]["text"][:300])

# ============================================================================
# CELL 5: Training
# ============================================================================
from trl import SFTTrainer
from transformers import TrainingArguments

print("\n🏋️ Starting fine-tuning...")
print(f"  Epochs: {TRAIN_EPOCHS}")
print(f"  Total steps: ~{len(formatted_dataset) * TRAIN_EPOCHS // (BATCH_SIZE * GRAD_ACCUM_STEPS)}")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=formatted_dataset,
    args=TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
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
        save_strategy="epoch",
        save_total_limit=2,
        optim="adamw_8bit",
        seed=42,
        report_to="none",  # Set to "wandb" if you want tracking
    ),
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,  # Pack multiple short examples into one sequence for efficiency
)

# Show GPU memory before training
gpu_stats = torch.cuda.get_device_properties(0)
reserved_mem = torch.cuda.max_memory_reserved() / 1e9
print(f"  GPU Memory Reserved: {reserved_mem:.2f} GB / {gpu_stats.total_mem / 1e9:.1f} GB")

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
print("""
📥 DOWNLOAD YOUR MODEL:
1. In the Kaggle output panel (right side), find:
   - /kaggle/working/hidayah-lm-gguf/unsloth.Q4_K_M.gguf (~4.5 GB)
   
2. Click the three dots (...) → Download

3. On your Windows machine:
   a. Install Ollama: winget install Ollama.Ollama
   b. Create a file called 'Modelfile' with:
      FROM ./unsloth.Q4_K_M.gguf
      PARAMETER temperature 0.3
      PARAMETER num_ctx 4096
      SYSTEM "You are Hidayah AI..."
   c. Run: ollama create hidayah-lm:7b -f Modelfile
   d. Test: ollama run hidayah-lm:7b

4. Connect to Hidayah AI:
   Add to your .env file:
     USE_LOCAL_LLM=true
     LOCAL_LLM_URL=http://localhost:11434/v1
     LOCAL_LLM_MODEL=hidayah-lm:7b
   
   Then: streamlit run app.py
""")
