#!/usr/bin/env python3
"""
Test the comprehensive insurance model

Tests the model's ability to answer questions about:
1. Insurance companies
2. Insurance documents  
3. Insurance products and target profiles
4. Insurance guarantees and coverage
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import os

def load_comprehensive_model(base_model_name, adapter_path):
    """Load the comprehensive trained model"""
    print("🔄 Loading comprehensive model...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Load and apply LoRA adapters
    print("🔄 Loading trained adapters...")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    
    return model, tokenizer

def generate_response(model, tokenizer, prompt, max_length=512):
    """Generate a response from the model"""
    # Format prompt similar to training format
    formatted_prompt = prompt + "\n\n###\n\n"
    
    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    # Decode response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the completion part
    if "###" in response:
        response = response.split("###")[-1].strip()
    
    # Remove END token if present
    if response.endswith(" END"):
        response = response[:-4].strip()
    
    return response

def test_comprehensive_model():
    """Test the comprehensive model with various question types"""
    
    # Configuration
    BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
    ADAPTER_PATH = "bhagent/outputs/sft_mistral_comprehensive"
    
    # Check if adapter exists
    if not os.path.exists(ADAPTER_PATH):
        print(f"❌ Model not found at {ADAPTER_PATH}")
        print("Please train the comprehensive model first using train_comprehensive_model.py")
        return
    
    print("🚀 Testing Comprehensive Insurance Model")
    print("=" * 60)
    
    # Load model
    try:
        model, tokenizer = load_comprehensive_model(BASE_MODEL, ADAPTER_PATH)
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Test queries covering all data types
    test_queries = [
        # Company data questions
        "Quelle est l'activité de la société Societe_000001?",
        "Où se trouve la société Societe_000002?",
        
        # Product mapping questions  
        "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
        "À quelle branche appartient le produit ASSURANCE MIXTE VIE?",
        "Quels sont les produits disponibles dans la branche VIE?",
        "Qui devrait acheter le produit ASSURANCE HOMME CLEF?",
        
        # Guarantee questions
        "Que couvre la garantie DECES?",
        "Quelles sont les garanties disponibles pour le produit TEMPORAIRE DECES?",
        "Pouvez-vous expliquer la garantie INVALIDITE PERMANENTE TOTALE?",
        "Quel produit offre la garantie INCAPACITE TEMPORAIRE DE TRAVAIL?",
        
        # PDF document questions
        "Que contient le document ASSURANCE BRIS DE GLACES?",
        "Quelles sont les conditions générales pour MULTIRISQUE HABITATION?",
        
        # Mixed questions
        "Quels sont les différents types d'assurance vie disponibles?",
        "Comment choisir une assurance pour une entreprise?",
        "Quelles garanties sont importantes pour un emprunteur?"
    ]
    
    print("\n🧪 Testing comprehensive model:")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Question {i}: {query}")
        print("-" * 50)
        
        try:
            response = generate_response(model, tokenizer, query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error generating response: {e}")
        
        print()

def interactive_comprehensive_test():
    """Interactive testing mode for comprehensive model"""
    BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
    ADAPTER_PATH = "bhagent/outputs/sft_mistral_comprehensive"
    
    if not os.path.exists(ADAPTER_PATH):
        print(f"❌ Model not found at {ADAPTER_PATH}")
        return
    
    print("🚀 Interactive Comprehensive Insurance Model Testing")
    print("=" * 60)
    
    try:
        model, tokenizer = load_comprehensive_model(BASE_MODEL, ADAPTER_PATH)
        print("✅ Model loaded successfully!")
        print("\n💬 Ask questions about:")
        print("  📊 Insurance companies")
        print("  📄 Insurance documents")
        print("  🎯 Insurance products and target profiles")
        print("  🛡️ Insurance guarantees and coverage")
        print("\nType 'quit' to exit")
        print("-" * 60)
        
        while True:
            query = input("\n🔍 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            try:
                response = generate_response(model, tokenizer, query)
                print(f"🤖 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error loading model: {e}")

def show_training_data_summary():
    """Show summary of what data the model was trained on"""
    print("📊 Training Data Summary")
    print("=" * 40)
    
    data_files = [
        ("Company Data", "bhagent/data/assurance_training_data.jsonl"),
        ("PDF Documents", "bhagent/data/pdf_training_data.jsonl"),
        ("Products & Guarantees", "bhagent/data/new_excel_training_data.jsonl")
    ]
    
    total_examples = 0
    
    for name, file_path in data_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f)
            print(f"✅ {name}: {count} examples")
            total_examples += count
        else:
            print(f"❌ {name}: File not found")
    
    print(f"\n📈 Total Training Examples: {total_examples}")
    
    # Show sample data from new Excel files
    new_excel_file = "bhagent/data/new_excel_data.json"
    if os.path.exists(new_excel_file):
        with open(new_excel_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n🔍 Sample questions from new Excel data:")
        for i, example in enumerate(data[:3]):
            prompt = example['prompt'].replace('\n\n###\n\n', '').strip()
            completion = example['completion'].replace(' END', '').strip()
            print(f"{i+1}. Q: {prompt}")
            print(f"   A: {completion}")
            print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_comprehensive_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "--summary":
        show_training_data_summary()
    else:
        # Show training data summary first
        show_training_data_summary()
        
        # Run automated tests
        test_comprehensive_model()
        
        print("\n" + "=" * 60)
        print("💡 Usage options:")
        print("   python scripts/test_comprehensive_model.py --interactive")
        print("   python scripts/test_comprehensive_model.py --summary")
