#!/usr/bin/env python3
"""
CPU-based training for client data
This script trains on CPU to avoid GPU memory issues
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
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main training function"""
    
    print("🔐 CPU Client Data Training")
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
    
    # Use a smaller model for CPU training
    model_name = "microsoft/DialoGPT-small"  # Much smaller model
    print(f"🔄 Loading small model for CPU training: {model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # Load model on CPU
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,  # Use float32 for CPU
        device_map=None,            # Don't use device_map
    )
    
    # Move to CPU explicitly
    model = model.to('cpu')
    
    print(f"✅ Model loaded on CPU")
    
    # Load dataset - use only a small subset for demonstration
    print("📊 Loading client dataset...")
    dataset = load_dataset("json", data_files=client_data_file)["train"]
    
    # Take only first 100 examples for CPU training
    dataset = dataset.select(range(min(100, len(dataset))))
    print(f"✅ Using {len(dataset)} examples for CPU training")
    
    def tokenize_function(examples):
        # Combine prompt and completion
        texts = [prompt + completion for prompt, completion in 
                zip(examples["prompt"], examples["completion"])]
        
        # Tokenize with shorter sequences
        tokenized = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=128,  # Very short sequences for CPU
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
    output_dir = "outputs/client_cpu_model"
    os.makedirs(output_dir, exist_ok=True)
    
    # Training arguments for CPU
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,              # Just 1 epoch for demo
        per_device_train_batch_size=1,   # Very small batch
        gradient_accumulation_steps=2,   # Effective batch size = 2
        learning_rate=5e-5,              # Lower learning rate
        warmup_steps=5,
        logging_steps=5,
        save_steps=50,
        save_total_limit=1,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        fp16=False,                      # No FP16 on CPU
        use_cpu=True,                    # Force CPU usage
        report_to=None,
        push_to_hub=False,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Train
    print("🔥 Starting CPU training (this will be slow)...")
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
            "method": "CPU fine-tuning on client data",
            "device": "CPU"
        }
        
        with open(os.path.join(output_dir, "training_info.json"), 'w') as f:
            json.dump(info, f, indent=2)
        
        print("✅ Training completed successfully!")
        print(f"📁 Model saved to: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model():
    """Test the trained model"""
    
    model_path = "outputs/client_cpu_model"
    if not os.path.exists(model_path):
        print("❌ Trained model not found")
        return
    
    print("🧪 Testing trained model...")
    
    try:
        from transformers import pipeline
        
        # Load the trained model
        generator = pipeline(
            'text-generation',
            model=model_path,
            tokenizer=model_path,
            device=-1  # CPU
        )
        
        # Test questions
        test_questions = [
            "What is the profession of Ben Ali El Amri Ahmed Salah?",
            "Who is Ben Ali El Amri Ahmed Salah?",
        ]
        
        for question in test_questions:
            print(f"\nQ: {question}")
            try:
                response = generator(
                    question,
                    max_length=50,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                print(f"A: {response[0]['generated_text']}")
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"❌ Testing failed: {e}")

if __name__ == "__main__":
    print("⚠️ This script uses CPU training which is slow but works with limited GPU memory")
    print("🔄 Training on a small subset of data for demonstration")
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Client model trained on CPU!")
        print("\nTesting the model...")
        test_model()
        
        print("\nNext steps:")
        print("1. The model is saved in: outputs/client_cpu_model")
        print("2. You can use it in your chat service")
        print("3. For production, consider using a GPU server or cloud training")
    else:
        print("\n❌ Training failed")
