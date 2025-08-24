#!/usr/bin/env python3
"""
Train comprehensive insurance model on all data sources

This script combines training data from:
1. Original Excel insurance company data (2,080 examples)
2. PDF insurance documents (268 examples)  
3. New Excel files - Product mapping & Guarantees (1,725 examples)

Total: ~4,000+ training examples covering:
- Company information
- Insurance documents
- Product profiles and target customers
- Guarantee descriptions and coverage details
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

def combine_all_training_data():
    """Combine all available training data sources"""
    print("🔄 Combining all training data sources...")
    
    data_files = []
    data_descriptions = []
    
    # Original Excel company data
    excel_file = "bhagent/data/assurance_training_data.jsonl"
    if os.path.exists(excel_file):
        data_files.append(excel_file)
        data_descriptions.append("Company data")
        print(f"✅ Found company data: {excel_file}")
    
    # PDF documents data
    pdf_file = "bhagent/data/pdf_training_data.jsonl"
    if os.path.exists(pdf_file):
        data_files.append(pdf_file)
        data_descriptions.append("PDF documents")
        print(f"✅ Found PDF data: {pdf_file}")
    
    # New Excel files data (products & guarantees)
    new_excel_file = "bhagent/data/new_excel_training_data.jsonl"
    if os.path.exists(new_excel_file):
        data_files.append(new_excel_file)
        data_descriptions.append("Products & Guarantees")
        print(f"✅ Found new Excel data: {new_excel_file}")
    
    if not data_files:
        print("❌ No training data found!")
        return None, []
    
    # Load and combine datasets
    datasets = []
    total_examples = 0
    
    for i, file_path in enumerate(data_files):
        dataset = load_dataset("json", data_files=file_path)["train"]
        datasets.append(dataset)
        total_examples += len(dataset)
        print(f"   📊 {data_descriptions[i]}: {len(dataset)} examples")
    
    # Combine all datasets
    if len(datasets) > 1:
        combined_dataset = concatenate_datasets(datasets)
        print(f"✅ Combined dataset: {len(combined_dataset)} total examples")
    else:
        combined_dataset = datasets[0]
        print(f"✅ Using single dataset: {len(combined_dataset)} examples")
    
    return combined_dataset, data_descriptions

def main():
    print("🚀 Training Comprehensive Insurance Model")
    print("=" * 70)
    
    # Check GPU
    print("Checking GPU availability...")
    print("Is CUDA available?:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU Name:", torch.cuda.get_device_name(0))
        print("CUDA Version:", torch.version.cuda)
    
    # Configuration
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
    OUTPUT_DIR = "bhagent/outputs/sft_mistral_comprehensive"
    OFFLOAD_DIR = "bhagent/outputs/offload"
    
    BATCH_SIZE = 1
    NUM_EPOCHS = 2  # Reduced for faster training
    LEARNING_RATE = 2e-4
    MAX_LENGTH = 256  # Reduced for memory efficiency
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OFFLOAD_DIR, exist_ok=True)
    
    # Combine all training data
    combined_dataset, data_sources = combine_all_training_data()
    if combined_dataset is None:
        return 1
    
    print(f"\n📊 Comprehensive Training Dataset:")
    print(f"   📈 Total examples: {len(combined_dataset)}")
    print(f"   📋 Data sources: {', '.join(data_sources)}")
    
    # Load tokenizer and model
    print("\n🔄 Loading tokenizer and model...")
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
    
    # Show sample data from different sources
    print("\n📋 Sample training examples:")
    sample_indices = [0, len(combined_dataset)//3, 2*len(combined_dataset)//3]
    for i, idx in enumerate(sample_indices):
        if idx < len(combined_dataset):
            example = combined_dataset[idx]
            print(f"\nExample {i+1} (index {idx}):")
            print(f"  Prompt: {example['prompt'][:80]}...")
            print(f"  Completion: {example['completion'][:80]}...")
    
    # Tokenize function
    def tokenize_fn(example):
        text = example["prompt"] + example["completion"]
        return tokenizer(text, truncation=True, max_length=MAX_LENGTH)
    
    print("\n🔄 Tokenizing dataset...")
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
        save_steps=200,  # Save more frequently for large dataset
        logging_steps=20,
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
    print("\n🎯 Starting comprehensive training...")
    print(f"📊 Training examples: {len(combined_dataset)}")
    print(f"🎯 Output directory: {OUTPUT_DIR}")
    print(f"⚙️ Epochs: {NUM_EPOCHS}")
    print(f"📏 Max length: {MAX_LENGTH}")
    print(f"📋 Data sources: {len(data_sources)}")
    print("=" * 70)
    
    # Check for existing checkpoints
    checkpoint_dir = None
    for cp in ["checkpoint-600", "checkpoint-400", "checkpoint-200"]:
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
    
    print(f"\n✅ Comprehensive training completed!")
    print(f"🎯 Model saved to: {OUTPUT_DIR}")
    print("\n🎉 Your comprehensive insurance model is ready!")
    print("\nYour model can now answer questions about:")
    print("  📊 Insurance companies and their details")
    print("  📄 Insurance policy documents and conditions")
    print("  🎯 Insurance products and target profiles")
    print("  🛡️ Insurance guarantees and coverage details")

if __name__ == "__main__":
    main()
