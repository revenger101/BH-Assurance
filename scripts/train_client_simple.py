#!/usr/bin/env python3
"""
Simple incremental training on client data using base Mistral model
This script trains only on client data while preserving existing knowledge
"""

import os
import torch
import json
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from datasets import Dataset, load_dataset
from peft import LoraConfig, get_peft_model, TaskType
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main training function"""
    
    print("🔐 Simple Client Data Training")
    print("=" * 50)
    
    # Check client data
    client_data_file = "bhagent/data/client_training_data.jsonl"
    if not os.path.exists(client_data_file):
        print(f"❌ Client data not found: {client_data_file}")
        return False
    
    # Count examples
    with open(client_data_file, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    print(f"✅ Found {line_count} client training examples")
    
    # Use base Mistral model
    model_name = "mistralai/Mistral-7B-Instruct-v0.1"
    print(f"🔄 Loading base model: {model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,                     # Smaller rank for efficiency
        lora_alpha=16,           # Scaling parameter
        lora_dropout=0.1,        # Dropout for regularization
        target_modules=["q_proj", "v_proj"],  # Simplified target modules
        bias="none",
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load dataset
    print("📊 Loading client dataset...")
    dataset = load_dataset("json", data_files=client_data_file)["train"]
    
    # Take a smaller subset for faster training (first 1000 examples)
    dataset = dataset.select(range(min(1000, len(dataset))))
    print(f"✅ Using {len(dataset)} examples for training")
    
    def tokenize_function(examples):
        # Combine prompt and completion
        texts = [prompt + completion for prompt, completion in 
                zip(examples["prompt"], examples["completion"])]
        
        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding=False,
            max_length=256,  # Shorter sequences for faster training
            return_tensors=None
        )
        
        # Set labels
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
    
    # Tokenize dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing"
    )
    
    # Output directory
    output_dir = "outputs/client_simple_model"
    os.makedirs(output_dir, exist_ok=True)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=2,              # Fewer epochs
        per_device_train_batch_size=2,   # Larger batch size
        gradient_accumulation_steps=4,   # Effective batch size = 8
        learning_rate=2e-4,              # Standard learning rate
        warmup_steps=10,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        fp16=True,                       # Use FP16 for efficiency
        report_to=None,                  # Disable wandb
        push_to_hub=False,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        pad_to_multiple_of=8,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # Train
    print("🔥 Starting training...")
    try:
        trainer.train()
        
        # Save model
        print("💾 Saving model...")
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        
        # Save training info
        info = {
            "base_model": model_name,
            "training_examples": len(tokenized_dataset),
            "epochs": training_args.num_train_epochs,
            "learning_rate": training_args.learning_rate,
            "method": "LoRA fine-tuning on client data"
        }
        
        with open(os.path.join(output_dir, "training_info.json"), 'w') as f:
            json.dump(info, f, indent=2)
        
        print("✅ Training completed successfully!")
        print(f"📁 Model saved to: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Check CUDA
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
    else:
        print("⚠️ CUDA not available, using CPU")
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Client model trained!")
        print("\nNext steps:")
        print("1. Test the model:")
        print("   python -c \"from transformers import pipeline; pipe = pipeline('text-generation', 'outputs/client_simple_model'); print(pipe('What is the profession of Ben Ali El Amri Ahmed Salah?'))\"")
        print("2. Update chat service to use: outputs/client_simple_model")
    else:
        print("\n❌ Training failed")
