#!/usr/bin/env python3
"""
Quick Model Testing Script

This script provides a simpler way to test the model without complex loading.
It uses the existing test script from the scripts directory.
"""

import subprocess
import sys
import os
from pathlib import Path

def test_model_with_questions():
    """Test the model with predefined questions"""
    
    print("🚀 Quick Model Testing for BH Insurance")
    print("=" * 50)
    
    # Test questions covering all data types
    test_questions = [
        # Company data questions
        "Quelle est l'activité de la société Societe_000001?",
        "Où se trouve la société Societe_000002?",
        "Quel est le matricule fiscal de Societe_000003?",
        
        # Product mapping questions
        "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
        "À quelle branche appartient le produit ASSURANCE MIXTE VIE?",
        "Qui devrait acheter le produit ASSURANCE HOMME CLEF?",
        
        # Guarantee questions
        "Que couvre la garantie DECES?",
        "Quelles sont les garanties disponibles pour le produit TEMPORAIRE DECES?",
        "Pouvez-vous expliquer la garantie INVALIDITE PERMANENTE TOTALE?",
        
        # PDF document questions
        "Que contient le document ASSURANCE BRIS DE GLACES?",
        "Quelles sont les conditions générales pour MULTIRISQUE HABITATION?",
        
        # General insurance questions
        "Quels sont les différents types d'assurance vie disponibles?",
        "Comment choisir une assurance pour une entreprise?",
        "Quelles garanties sont importantes pour un emprunteur?",
        
        # Edge cases
        "Société inexistante XYZ123?",
        "Bonjour comment allez-vous?"
    ]
    
    print(f"📋 Testing {len(test_questions)} questions...")
    print("=" * 50)
    
    # Check if the test script exists
    test_script = Path("bhagent/scripts/test_comprehensive_model.py")
    if not test_script.exists():
        print(f"❌ Test script not found: {test_script}")
        return False
    
    # Run the test script
    try:
        print("🔄 Running model test script...")
        result = subprocess.run([
            sys.executable, str(test_script)
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Model test completed successfully!")
            print("\nOutput:")
            print(result.stdout)
        else:
            print("❌ Model test failed!")
            print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def check_model_files():
    """Check if model files exist"""
    print("🔍 Checking model files...")
    
    model_paths = [
        "bhagent/outputs/sft_mistral_combined/checkpoint-882",
        "bhagent/outputs/sft_mistral_insurance/checkpoint-780",
        "bhagent/outputs/sft_mistral_comprehensive/checkpoint-1530"
    ]
    
    available_models = []
    
    for model_path in model_paths:
        path = Path(model_path)
        if path.exists():
            # Check for adapter files
            adapter_config = path / "adapter_config.json"
            adapter_model = path / "adapter_model.safetensors"
            
            if adapter_config.exists() and adapter_model.exists():
                available_models.append(model_path)
                print(f"✅ Found complete model: {model_path}")
            else:
                print(f"⚠️ Incomplete model: {model_path}")
        else:
            print(f"❌ Model not found: {model_path}")
    
    return available_models

def check_training_data():
    """Check training data files"""
    print("\n📊 Checking training data...")
    
    data_files = [
        ("Company Data", "bhagent/data/assurance_training_data.jsonl"),
        ("PDF Documents", "bhagent/data/pdf_training_data.jsonl"),
        ("Products & Guarantees", "bhagent/data/new_excel_training_data.jsonl"),
        ("Raw Company Data", "bhagent/data/assurance_data.json"),
        ("Raw PDF Data", "bhagent/data/pdf_extracted_text.json"),
        ("Raw New Excel Data", "bhagent/data/new_excel_data.json")
    ]
    
    total_examples = 0
    
    for name, file_path in data_files:
        path = Path(file_path)
        if path.exists():
            if file_path.endswith('.jsonl'):
                with open(path, 'r', encoding='utf-8') as f:
                    count = sum(1 for _ in f)
                print(f"✅ {name}: {count} examples")
                total_examples += count
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                    else:
                        count = len(data) if isinstance(data, dict) else 1
                print(f"✅ {name}: {count} records")
        else:
            print(f"❌ {name}: Not found")
    
    print(f"\n📈 Total Training Examples: {total_examples}")
    return total_examples > 0

def manual_test_questions():
    """Provide manual testing instructions"""
    print("\n🧪 Manual Testing Instructions")
    print("=" * 40)
    
    print("Since automated testing requires significant memory, here are manual test options:")
    print("\n1. **Interactive Testing:**")
    print("   python bhagent/scripts/test_comprehensive_model.py --interactive")
    
    print("\n2. **Test Specific Questions:**")
    sample_questions = [
        "Quelle est l'activité de la société Societe_000001?",
        "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
        "Que couvre la garantie DECES?",
        "Que contient le document ASSURANCE BRIS DE GLACES?"
    ]
    
    for i, question in enumerate(sample_questions, 1):
        print(f"   {i}. {question}")
    
    print("\n3. **Expected Response Quality:**")
    print("   ✅ Good: Specific, relevant answers with correct terminology")
    print("   ⚠️ Fair: General answers that show some knowledge")
    print("   ❌ Poor: Irrelevant or incorrect responses")

def show_model_performance_summary():
    """Show expected model performance based on training data"""
    print("\n📊 Expected Model Performance")
    print("=" * 40)
    
    print("Based on your training data, the model should be able to answer:")
    
    print("\n🏢 **Company Information (2,080 examples):**")
    print("   • Company activities and sectors")
    print("   • Company locations (cities, governorates)")
    print("   • Fiscal information (matricule fiscal)")
    print("   • Business sector classifications")
    
    print("\n📄 **Insurance Documents (268 examples):**")
    print("   • Policy conditions and terms")
    print("   • Coverage details")
    print("   • Insurance product information")
    print("   • Legal and regulatory content")
    
    print("\n🎯 **Products & Guarantees (1,725 examples):**")
    print("   • Product target profiles")
    print("   • Insurance branches and sub-branches")
    print("   • Guarantee descriptions and coverage")
    print("   • Product recommendations")
    
    print("\n🎯 **Overall Capabilities:**")
    print("   • Total training examples: ~4,073")
    print("   • Covers: Companies, Products, Guarantees, Documents")
    print("   • Languages: French (primary)")
    print("   • Domain: Tunisian insurance market")

def main():
    """Main testing function"""
    print("🚀 BH Insurance Model Quick Test")
    print("=" * 50)
    
    # Check model files
    available_models = check_model_files()
    
    if not available_models:
        print("\n❌ No trained models found!")
        print("Please ensure model training completed successfully.")
        return 1
    
    print(f"\n✅ Found {len(available_models)} trained model(s)")
    
    # Check training data
    if not check_training_data():
        print("\n❌ Training data not found!")
        return 1
    
    # Show performance summary
    show_model_performance_summary()
    
    # Provide manual testing instructions
    manual_test_questions()
    
    print("\n🎯 **Recommended Next Steps:**")
    print("1. Try interactive testing with your best model")
    print("2. Test with questions from different categories")
    print("3. Evaluate response quality and relevance")
    print("4. Note any areas where the model needs improvement")
    
    print("\n🎉 Your model is ready for testing!")
    print("Use the interactive mode to evaluate its performance.")
    
    return 0

if __name__ == "__main__":
    import json
    sys.exit(main())
