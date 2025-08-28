#!/usr/bin/env python3
"""
Incremental training on confidential client data
This script trains the model ONLY on new client data while preserving existing knowledge
"""

import os
import sys
import torch
import json
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from datasets import Dataset, load_dataset
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_client_data():
    """Check if client training data exists"""
    
    client_data_file = "bhagent/data/client_training_data.jsonl"
    
    if not os.path.exists(client_data_file):
        print("❌ Client training data not found!")
        print("Please run: python scripts/convert_client_data.py first")
        return None
    
    # Count examples
    with open(client_data_file, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    
    print(f"✅ Found client training data: {line_count} examples")
    return client_data_file

def find_best_existing_model():
    """Find the best existing trained model to use as base"""
    
    # Priority order of models to check
    model_paths = [
        "bhagent/outputs/sft_mistral_comprehensive",  # Most comprehensive
        "bhagent/outputs/sft_mistral_combined",       # Combined training
        "bhagent/outputs/sft_mistral_insurance",      # Insurance specific
        "bhagent/outputs/sft_mistral",                # Basic training
        "outputs/sft_mistral_comprehensive",          # Alternative paths
        "outputs/sft_mistral_combined",
        "outputs/sft_mistral_insurance",
        "outputs/sft_mistral",
    ]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"✅ Found existing trained model: {model_path}")
            return model_path
    
    print("⚠️ No existing trained model found, using base model")
    return "mistralai/Mistral-7B-Instruct-v0.1"

def setup_model_and_tokenizer(model_path):
    """Setup model and tokenizer with LoRA for efficient training"""
    
    print(f"🔄 Loading model from: {model_path}")
    
    # Quantization config for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    )
    
    # LoRA configuration for incremental learning
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=16,                    # Rank - balance between efficiency and capacity
        lora_alpha=32,           # Scaling parameter
        lora_dropout=0.1,        # Dropout for regularization
        target_modules=[         # Target attention modules
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        bias="none",
    )
    
    # Apply LoRA to model
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    return model, tokenizer

def prepare_dataset(data_file, tokenizer):
    """Prepare dataset for training"""
    
    print(f"📊 Preparing dataset from: {data_file}")
    
    # Load dataset
    dataset = load_dataset("json", data_files=data_file)["train"]
    print(f"✅ Loaded {len(dataset)} training examples")
    
    def tokenize_function(examples):
        # Combine prompt and completion
        texts = [prompt + completion for prompt, completion in 
                zip(examples["prompt"], examples["completion"])]
        
        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding=False,
            max_length=512,
            return_tensors=None
        )
        
        # Set labels (for causal language modeling, labels = input_ids)
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    # Tokenize dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing client data"
    )
    
    return tokenized_dataset

def train_incremental_model():
    """Main training function for incremental learning"""
    
    print("🔐 Starting incremental training on client data...")
    print("=" * 60)
    
    # Check client data
    client_data_file = check_client_data()
    if not client_data_file:
        return False
    
    # Find existing model
    base_model_path = find_best_existing_model()
    
    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(base_model_path)
    
    # Prepare dataset
    train_dataset = prepare_dataset(client_data_file, tokenizer)
    
    # Output directory
    output_dir = "outputs/client_incremental_model"
    os.makedirs(output_dir, exist_ok=True)
    
    # Training arguments optimized for incremental learning
    training_args = TrainingArguments(
        output_dir=output_dir,
        
        # Training schedule
        num_train_epochs=3,              # Fewer epochs to avoid forgetting
        per_device_train_batch_size=1,   # Small batch size
        gradient_accumulation_steps=8,   # Effective batch size = 8
        
        # Learning rate (lower to preserve existing knowledge)
        learning_rate=1e-5,              # Lower learning rate
        warmup_steps=20,
        lr_scheduler_type="cosine",
        
        # Optimization
        optim="adamw_torch",
        weight_decay=0.01,
        max_grad_norm=1.0,
        
        # Logging and saving
        logging_steps=5,
        save_steps=50,
        save_total_limit=3,
        
        # Evaluation
        evaluation_strategy="no",        # No evaluation for incremental training
        
        # Memory optimization
        dataloader_pin_memory=False,
        remove_unused_columns=False,
        
        # Mixed precision
        fp16=False,
        bf16=True,
        
        # Other settings
        report_to=None,                  # Disable wandb/tensorboard
        push_to_hub=False,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Causal language modeling
        pad_to_multiple_of=8,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # Start training
    print("🔥 Starting incremental training...")
    print(f"📊 Training on {len(train_dataset)} client examples")
    print(f"🎯 Output directory: {output_dir}")
    
    try:
        # Train the model
        trainer.train()
        
        # Save the final model
        print("💾 Saving trained model...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        
        print("✅ Incremental training completed successfully!")
        print(f"📁 Model saved to: {output_dir}")
        
        # Save training info
        info = {
            "base_model": base_model_path,
            "training_data": client_data_file,
            "training_examples": len(train_dataset),
            "epochs": training_args.num_train_epochs,
            "learning_rate": training_args.learning_rate,
            "method": "LoRA incremental training"
        }
        
        with open(os.path.join(output_dir, "training_info.json"), 'w') as f:
            json.dump(info, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        return False

def main():
    """Main function"""
    
    print("🚀 Client Data Incremental Training")
    print("=" * 60)
    print("This script will:")
    print("1. Load your existing trained model")
    print("2. Apply LoRA for efficient incremental learning")
    print("3. Train ONLY on new client data")
    print("4. Preserve all existing insurance knowledge")
    print("=" * 60)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
        print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("⚠️ CUDA not available, using CPU (will be slow)")
    
    # Start training
    success = train_incremental_model()
    
    if success:
        print("\n🎉 SUCCESS! Client data training completed!")
        print("\nNext steps:")
        print("1. Update your chat service to use the new model:")
        print("   MODEL_PATH = 'outputs/client_incremental_model'")
        print("2. Test with client questions like:")
        print("   'What is the profession of Ben Ali El Amri Ahmed Salah?'")
        print("3. Verify existing insurance knowledge is preserved")
    else:
        print("\n❌ Training failed. Please check the logs above.")

if __name__ == "__main__":
    main()
