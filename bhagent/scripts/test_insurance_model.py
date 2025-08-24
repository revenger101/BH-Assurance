import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import os

def load_trained_model(base_model_name, adapter_path):
    """
    Load the base model and apply the trained LoRA adapters
    """
    print("🔄 Loading base model...")
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

def generate_response(model, tokenizer, prompt, max_length=256):
    """
    Generate a response from the model
    """
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

def test_insurance_queries():
    """
    Test the model with various insurance-related queries
    """
    
    # Configuration
    BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
    ADAPTER_PATH = "outputs/sft_mistral_insurance"
    
    # Check if adapter exists
    if not os.path.exists(ADAPTER_PATH):
        print(f"❌ Adapter not found at {ADAPTER_PATH}")
        print("Please train the model first using train_on_insurance_data.py")
        return
    
    print("🚀 Testing Insurance Model")
    print("=" * 50)
    
    # Load model
    try:
        model, tokenizer = load_trained_model(BASE_MODEL, ADAPTER_PATH)
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Test queries
    test_queries = [
        "Quelle est l'activité de la société Societe_000001?",
        "Où se trouve la société Societe_000002?",
        "Quel est le matricule fiscal de societe_000003?",
        "Dans quel gouvernorat se trouve Societe_000004?",
        "Quelles sont les entreprises dans le secteur SERVICES PERSONNELS?",
        "Donnez-moi des informations sur une société de CRÉDIT BAIL",
        "Quelles sont les activités dans le secteur INTERMÉDIATION FINANCIÈRE?",
        "Listez les entreprises à SFAX"
    ]
    
    print("\n🧪 Testing queries:")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 40)
        
        try:
            response = generate_response(model, tokenizer, query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error generating response: {e}")
        
        print()

def interactive_test():
    """
    Interactive testing mode
    """
    BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
    ADAPTER_PATH = "outputs/sft_mistral_insurance"
    
    if not os.path.exists(ADAPTER_PATH):
        print(f"❌ Adapter not found at {ADAPTER_PATH}")
        return
    
    print("🚀 Interactive Insurance Model Testing")
    print("=" * 50)
    
    try:
        model, tokenizer = load_trained_model(BASE_MODEL, ADAPTER_PATH)
        print("✅ Model loaded successfully!")
        print("\n💬 Enter your questions about insurance companies (type 'quit' to exit):")
        print("-" * 50)
        
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

def load_sample_data():
    """
    Load some sample data to show what the model was trained on
    """
    try:
        with open("data/assurance_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📊 Sample companies in the dataset:")
        print("-" * 40)
        
        for i, company in enumerate(data[:5]):
            print(f"{i+1}. {company['RAISON_SOCIALE']}")
            print(f"   Secteur: {company['LIB_SECTEUR_ACTIVITE']}")
            print(f"   Activité: {company['LIB_ACTIVITE']}")
            print(f"   Ville: {company['VILLE'] or 'Non spécifiée'}")
            print()
            
    except Exception as e:
        print(f"❌ Could not load sample data: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        # Show sample data first
        load_sample_data()
        
        # Run automated tests
        test_insurance_queries()
        
        print("\n" + "=" * 50)
        print("💡 Tip: Run with --interactive flag for interactive testing")
        print("   python scripts/test_insurance_model.py --interactive")
