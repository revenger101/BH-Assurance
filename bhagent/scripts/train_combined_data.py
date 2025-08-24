#!/usr/bin/env python3
"""
Train model on combined Excel and PDF data

This script combines training data from:
1. Excel insurance company data
2. PDF insurance documents (with OCR)
"""

import os
import torch
import json
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
    TrainingArguments,
)
from datasets import load_dataset, concatenate_datasets
from trl import SFTTrainer
from peft import LoraConfig, TaskType, prepare_model_for_kbit_training

def combine_training_data():
    """Combine Excel and PDF training data"""
    print("🔄 Combining training data sources...")
    
    data_files = []
    
    # Excel data
    excel_file = "bhagent/data/assurance_training_data.jsonl"
    if os.path.exists(excel_file):
        data_files.append(excel_file)
        print(f"✅ Found Excel training data: {excel_file}")
    else:
        print(f"⚠️ Excel training data not found: {excel_file}")
    
    # PDF data
    pdf_file = "bhagent/data/pdf_training_data.jsonl"
    if os.path.exists(pdf_file):
        data_files.append(pdf_file)
        print(f"✅ Found PDF training data: {pdf_file}")
    else:
        print(f"⚠️ PDF training data not found: {pdf_file}")
        print("   Run: python bhagent/data/extract_pdf_data.py to create it")
    
    if not data_files:
        print("❌ No training data found!")
        return None
    
    # Load and combine datasets
    datasets = []
    total_examples = 0
    
    for file_path in data_files:
        dataset = load_dataset("json", data_files=file_path)["train"]
        datasets.append(dataset)
        total_examples += len(dataset)
        print(f"   📊 {os.path.basename(file_path)}: {len(dataset)} examples")
    
    # Combine datasets
    if len(datasets) > 1:
        combined_dataset = concatenate_datasets(datasets)
        print(f"✅ Combined dataset: {len(combined_dataset)} total examples")
    else:
        combined_dataset = datasets[0]
        print(f"✅ Using single dataset: {len(combined_dataset)} examples")
    
    return combined_dataset

def main():
    print("🚀 Training Model on Combined Insurance Data")
    print("=" * 60)
    
    # Check GPU
    print("Checking GPU availability...")
    print("Is CUDA available?:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU Name:", torch.cuda.get_device_name(0))
        print("CUDA Version:", torch.version.cuda)
    
    # Configuration
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
    OUTPUT_DIR = "bhagent/outputs/sft_mistral_combined"
    OFFLOAD_DIR = "bhagent/outputs/offload"
    
    BATCH_SIZE = 1
    NUM_EPOCHS = 3
    LEARNING_RATE = 2e-4
    MAX_LENGTH = 512  # Increased for PDF content
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OFFLOAD_DIR, exist_ok=True)
    
    # Combine training data
    combined_dataset = combine_training_data()
    if combined_dataset is None:
        return 1
    
    # Load tokenizer and model
    print("🔄 Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    if DEVICE == "cuda":
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map={"": 0},
            quantization_config=quant_config,
            offload_folder=OFFLOAD_DIR
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="cpu",
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
    
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    
    # Shuffle dataset
    combined_dataset = combined_dataset.shuffle(seed=42)
    print(f"✅ Dataset shuffled: {len(combined_dataset)} examples")
    
    # Show sample data
    print("\n📋 Sample training examples:")
    for i, example in enumerate(combined_dataset.select(range(min(3, len(combined_dataset))))):
        print(f"Example {i+1}:")
        print(f"  Prompt: {example['prompt'][:100]}...")
        print(f"  Completion: {example['completion'][:100]}...")
        print()
    
    # Tokenize function
    def tokenize_fn(example):
        text = example["prompt"] + example["completion"]
        return tokenizer(text, truncation=True, max_length=MAX_LENGTH)
    
    print("🔄 Tokenizing dataset...")
    tokenized_dataset = combined_dataset.map(tokenize_fn, batched=False, 
                                           remove_columns=combined_dataset.column_names)
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    # LoRA Configuration
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    # Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        warmup_steps=50,
        save_steps=100,
        logging_steps=10,
        save_strategy="steps",
        fp16=True if DEVICE == "cuda" else False,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        max_grad_norm=0.3,
        dataloader_pin_memory=True if DEVICE == "cuda" else False,
        logging_dir=f"{OUTPUT_DIR}/logs",
    )
    
    # Initialize trainer
    print("🔧 Initializing trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        peft_config=lora_config,
        data_collator=data_collator,
    )
    
    # Start training
    print("🎯 Starting training on combined data...")
    print(f"📊 Training examples: {len(combined_dataset)}")
    print(f"🎯 Output directory: {OUTPUT_DIR}")
    print(f"⚙️ Epochs: {NUM_EPOCHS}")
    print(f"📏 Max length: {MAX_LENGTH}")
    print("=" * 60)
    
    trainer.train()
    
    print(f"✅ Training completed! Model saved to {OUTPUT_DIR}")
    print("🎉 Your model is now trained on both Excel and PDF data!")

if __name__ == "__main__":
    main()
