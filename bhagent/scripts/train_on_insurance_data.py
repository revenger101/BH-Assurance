import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
    TrainingArguments,
)
from datasets import load_dataset
from trl import SFTTrainer
from peft import LoraConfig, TaskType, prepare_model_for_kbit_training
import json

# -----------------------------
# 0. Basics & env
# -----------------------------
print("🚀 Starting Insurance Data Training...")
print("=" * 50)
print("Checking GPU availability...")
print("Is CUDA available?:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU Name:", torch.cuda.get_device_name(0))
    print("CUDA Version:", torch.version.cuda)
    print("Number of GPUs:", torch.cuda.device_count())
else:
    print("Warning: No CUDA device detected. Training will fall back to CPU - this will be slow!")

# small perf wins on RTX 20xx
torch.backends.cuda.matmul.allow_tf32 = True
try:
    torch.set_float32_matmul_precision("high")
except Exception:
    pass

# -----------------------------
# 1. Configuration
# -----------------------------
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# Use the new insurance training data
DATA_PATH = {
    "train": "bhagent/data/assurance_training_data.jsonl",
    "validation": "bhagent/data/qa_dataset_ft.jsonl"  # fallback to existing validation data
}

OUTPUT_DIR = "bhagent/outputs/sft_mistral_insurance"
OFFLOAD_DIR = "bhagent/outputs/offload"

BATCH_SIZE = 1         # 4 GB VRAM safe
NUM_EPOCHS = 3
LEARNING_RATE = 2e-4   # slightly lower for QLoRA stability
LR_WARMUP_STEPS = 50
SAVE_STEPS = 100
LOGGING_STEPS = 10
MAX_LENGTH = 256       # increased for insurance data

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OFFLOAD_DIR, exist_ok=True)

# -----------------------------
# 2. Verify data files exist
# -----------------------------
print("📋 Checking data files...")
for split, path in DATA_PATH.items():
    if os.path.exists(path):
        print(f"✅ {split} data found: {path}")
        # Count lines in JSONL file
        with open(path, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        print(f"   📊 Contains {line_count} examples")
    else:
        print(f"❌ {split} data not found: {path}")
        if split == "train":
            print("❌ Training data is required. Please run convert_excel_to_json.py first.")
            exit(1)

# -----------------------------
# 3. Load tokenizer and model (QLoRA 4-bit)
# -----------------------------
print("🔄 Loading tokenizer and model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

if DEVICE == "cuda":
    # QLoRA best-practice 4-bit quantization
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",          # QLoRA default
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )

    # Keep the whole quantized model on a single GPU to avoid CPU/CUDA mix
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map={"": 0},                 # all layers on cuda:0
        quantization_config=quant_config,
        offload_folder=OFFLOAD_DIR
    )
else:
    print("Loading model on CPU due to lack of CUDA support...")
    # CPU fallback (slow)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="cpu",
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )

# Prepare quantized model for k-bit training (PEFT util)
model = prepare_model_for_kbit_training(model)
model.config.use_cache = False  # must be False when gradient checkpointing is enabled

# -----------------------------
# 4. Load dataset
# -----------------------------
print("📚 Loading dataset...")
dataset = load_dataset("json", data_files=DATA_PATH)

# Optional shuffle for robustness
try:
    dataset["train"] = dataset["train"].shuffle(seed=42)
    print(f"✅ Training dataset shuffled: {len(dataset['train'])} examples")
except Exception as e:
    print(f"⚠️ Could not shuffle dataset: {e}")

# Show sample data
print("\n📋 Sample training examples:")
for i, example in enumerate(dataset["train"].select(range(min(3, len(dataset["train"]))))):
    print(f"Example {i+1}:")
    print(f"  Prompt: {example['prompt'][:100]}...")
    print(f"  Completion: {example['completion'][:100]}...")
    print()

# -----------------------------
# 5. Tokenize function
# -----------------------------
def tokenize_fn(example):
    text = example["prompt"] + example["completion"]
    return tokenizer(text, truncation=True, max_length=MAX_LENGTH)

print("🔄 Tokenizing dataset...")
tokenized_dataset = dataset.map(tokenize_fn, batched=False, remove_columns=dataset["train"].column_names)

# -----------------------------
# 6. Data collator
# -----------------------------
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# -----------------------------
# 7. LoRA Configuration (typical QLoRA values)
# -----------------------------
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # a bit broader than q/v only
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

# -----------------------------
# 8. Training Arguments (low-VRAM safe)
# -----------------------------
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    warmup_steps=LR_WARMUP_STEPS,
    save_steps=SAVE_STEPS,
    logging_steps=LOGGING_STEPS,
    save_strategy="steps",
    eval_steps=SAVE_STEPS,
    do_eval=True if "validation" in DATA_PATH and os.path.exists(DATA_PATH["validation"]) else False,
    fp16=True if DEVICE == "cuda" else False,
    bf16=False,
    gradient_accumulation_steps=8,       # accumulate to simulate larger batch
    gradient_checkpointing=True,         # big memory win
    optim="paged_adamw_8bit",            # bitsandbytes paged optimizer for memory
    max_grad_norm=0.3,

    dataloader_pin_memory=True if DEVICE == "cuda" else False,
    logging_dir=f"{OUTPUT_DIR}/logs",

    # avoid accidental multi-GPU settings on single-GPU Windows
    ddp_find_unused_parameters=None
)

# -----------------------------
# 9. Initialize trainer
# -----------------------------
print("🔧 Initializing trainer...")
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"] if "validation" in tokenized_dataset else None,
    peft_config=lora_config,
    data_collator=data_collator,
)

# -----------------------------
# 10. Start training
# -----------------------------
print("🎯 Starting fine-tuning on insurance data...")
print(f"📊 Training examples: {len(dataset['train'])}")
print(f"🎯 Output directory: {OUTPUT_DIR}")
print(f"⚙️ Epochs: {NUM_EPOCHS}")
print(f"📏 Max length: {MAX_LENGTH}")
print("=" * 50)

# Check for existing checkpoints
checkpoint_dir = None
for cp in ["checkpoint-300", "checkpoint-200", "checkpoint-100", "checkpoint-50"]:
    candidate = os.path.join(OUTPUT_DIR, cp)
    if os.path.isdir(candidate):
        checkpoint_dir = candidate
        break

if checkpoint_dir:
    print(f"🔄 Resuming from checkpoint: {checkpoint_dir}")
    trainer.train(resume_from_checkpoint=checkpoint_dir)
else:
    print("🆕 No checkpoint found, starting fresh training.")
    trainer.train()

print(f"✅ Training completed! Model + adapters saved to {OUTPUT_DIR}")
print("🎉 Your model is now trained on the insurance data!")
