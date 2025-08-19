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

# -----------------------------
# 0. Basics & env
# -----------------------------
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

DATA_PATH = {
    "train": "data/qa_dataset_ft_prepared.jsonl",
    "validation": "data/qa_dataset_ft.jsonl"
}

OUTPUT_DIR = "outputs/sft_mistral"
OFFLOAD_DIR = "outputs/offload"  # not used if we keep everything on one GPU, but left for completeness

BATCH_SIZE = 1         # 4 GB VRAM safe
NUM_EPOCHS = 3
LEARNING_RATE = 2e-4   # slightly lower for QLoRA stability
LR_WARMUP_STEPS = 50
SAVE_STEPS = 100
LOGGING_STEPS = 10
MAX_LENGTH = 128       # keep small on 4 GB GPUs

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OFFLOAD_DIR, exist_ok=True)

# -----------------------------
# 2. Load tokenizer and model (QLoRA 4-bit)
# -----------------------------
print("Loading tokenizer and model...")
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
    # (more stable on 4 GB than auto offload)
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
# (casts norms, sets up gradients, etc.)
model = prepare_model_for_kbit_training(model)
model.config.use_cache = False  # must be False when gradient checkpointing is enabled

# -----------------------------
# 3. Load dataset
# -----------------------------
print("Loading dataset...")
dataset = load_dataset("json", data_files=DATA_PATH)

# Optional shuffle for robustness
try:
    dataset["train"] = dataset["train"].shuffle(seed=42)
except Exception:
    pass

# -----------------------------
# 4. Tokenize function
# -----------------------------
def tokenize_fn(example):
    text = example["prompt"] + example["completion"]
    return tokenizer(text, truncation=True, max_length=MAX_LENGTH)

tokenized_dataset = dataset.map(tokenize_fn, batched=False, remove_columns=dataset["train"].column_names)

# -----------------------------
# 5. Data collator
# -----------------------------
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# -----------------------------
# 6. LoRA Configuration (typical QLoRA values)
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
# 7. Training Arguments (low-VRAM safe)
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
    do_eval=True if "validation" in DATA_PATH else False,
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
# 8. Initialize trainer
# -----------------------------
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"] if "validation" in DATA_PATH else None,
    peft_config=lora_config,
    data_collator=data_collator,
)

# -----------------------------
# 9. Start training (no manual load_adapter)
# -----------------------------
print("Starting fine-tuning...")

# If a checkpoint exists, let Trainer handle it. Do NOT call model.load_adapter().
checkpoint_dir = None
for cp in ["checkpoint-300", "checkpoint-200", "checkpoint-100", "checkpoint-50"]:
    candidate = os.path.join(OUTPUT_DIR, cp)
    if os.path.isdir(candidate):
        checkpoint_dir = candidate
        break

if checkpoint_dir:
    print(f"Resuming from checkpoint: {checkpoint_dir}")
    trainer.train(resume_from_checkpoint=None)
else:
    print("No checkpoint found, starting fresh.")
    trainer.train()

print(f"Model + adapters saved to {OUTPUT_DIR}")
