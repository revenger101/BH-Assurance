#!/usr/bin/env python3
"""
Simple Model Testing Script

Tests the model with a few key questions to evaluate performance
without requiring too much memory.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import time
import os

def test_model_simple():
    """Simple model test with key questions"""
    
    print("🚀 Simple Model Test for BH Insurance")
    print("=" * 50)
    
    # Model configuration
    BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
    MODEL_PATH = "bhagent/outputs/sft_mistral_combined/checkpoint-882"
    
    print(f"📍 Using model: {MODEL_PATH}")
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found: {MODEL_PATH}")
        return False
    
    try:
        print("🔄 Loading model (this may take a few minutes)...")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load base model with memory optimization
        print("Loading base model...")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
            offload_folder="bhagent/outputs/offload"
        )
        
        # Load trained adapters
        print("Loading trained adapters...")
        model = PeftModel.from_pretrained(model, MODEL_PATH)
        model.eval()
        
        print("✅ Model loaded successfully!")
        
        # Test questions
        test_questions = [
            {
                "question": "Quelle est l'activité de la société Societe_000001?",
                "category": "Company Data",
                "expected_keywords": ["société", "activité", "secteur"]
            },
            {
                "question": "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
                "category": "Product Mapping", 
                "expected_keywords": ["profils", "cibles", "emprunteurs"]
            },
            {
                "question": "Que couvre la garantie DECES?",
                "category": "Guarantees",
                "expected_keywords": ["garantie", "couvre", "deces"]
            },
            {
                "question": "Que contient le document ASSURANCE BRIS DE GLACES?",
                "category": "PDF Documents",
                "expected_keywords": ["document", "bris", "glaces"]
            },
            {
                "question": "Comment choisir une assurance pour une entreprise?",
                "category": "General Knowledge",
                "expected_keywords": ["assurance", "entreprise", "choisir"]
            }
        ]
        
        print(f"\n🧪 Testing {len(test_questions)} questions...")
        print("=" * 50)
        
        results = []
        
        for i, test in enumerate(test_questions, 1):
            question = test["question"]
            category = test["category"]
            expected_keywords = test["expected_keywords"]
            
            print(f"\n📝 Test {i}: {category}")
            print(f"Question: {question}")
            
            # Generate response
            start_time = time.time()
            response = generate_response(model, tokenizer, question)
            generation_time = time.time() - start_time
            
            print(f"Response: {response}")
            print(f"Time: {generation_time:.2f}s")
            
            # Simple evaluation
            score = evaluate_response(question, response, expected_keywords)
            print(f"Score: {score}/100")
            
            results.append({
                "question": question,
                "response": response,
                "score": score,
                "time": generation_time,
                "category": category
            })
            
            # Small delay
            time.sleep(2)
        
        # Summary
        print_summary(results)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def generate_response(model, tokenizer, prompt, max_length=256):
    """Generate response from model"""
    try:
        # Format prompt
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
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract completion
        if "###" in response:
            response = response.split("###")[-1].strip()
        
        if response.endswith(" END"):
            response = response[:-4].strip()
        
        return response
        
    except Exception as e:
        return f"Error generating response: {str(e)}"

def evaluate_response(question, response, expected_keywords):
    """Simple response evaluation"""
    score = 0
    
    # Basic checks
    if len(response) < 10:
        return 10  # Too short
    
    if "Error" in response:
        return 0  # Generation error
    
    # Length check
    if len(response) > 20:
        score += 30
    
    # Keyword check
    found_keywords = 0
    for keyword in expected_keywords:
        if keyword.lower() in response.lower():
            found_keywords += 1
    
    if expected_keywords:
        keyword_score = (found_keywords / len(expected_keywords)) * 40
        score += keyword_score
    
    # Relevance check (basic)
    question_words = set(question.lower().split())
    response_words = set(response.lower().split())
    common_words = question_words.intersection(response_words)
    
    if len(common_words) > 2:
        score += 30
    
    return min(score, 100)

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if not results:
        print("❌ No results to summarize")
        return
    
    # Overall stats
    total_tests = len(results)
    avg_score = sum(r["score"] for r in results) / total_tests
    avg_time = sum(r["time"] for r in results) / total_tests
    
    print(f"📈 Total Tests: {total_tests}")
    print(f"📊 Average Score: {avg_score:.1f}/100")
    print(f"⏱️ Average Time: {avg_time:.2f}s")
    
    # Score distribution
    excellent = sum(1 for r in results if r["score"] >= 80)
    good = sum(1 for r in results if 60 <= r["score"] < 80)
    fair = sum(1 for r in results if 40 <= r["score"] < 60)
    poor = sum(1 for r in results if r["score"] < 40)
    
    print(f"\n📊 Performance Distribution:")
    print(f"🟢 Excellent (80-100): {excellent}/{total_tests} ({excellent/total_tests*100:.1f}%)")
    print(f"🟡 Good (60-79): {good}/{total_tests} ({good/total_tests*100:.1f}%)")
    print(f"🟠 Fair (40-59): {fair}/{total_tests} ({fair/total_tests*100:.1f}%)")
    print(f"🔴 Poor (0-39): {poor}/{total_tests} ({poor/total_tests*100:.1f}%)")
    
    # Category breakdown
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result["score"])
    
    print(f"\n📊 Category Performance:")
    for category, scores in categories.items():
        avg_cat_score = sum(scores) / len(scores)
        print(f"   {category}: {avg_cat_score:.1f}/100")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if avg_score >= 80:
        print("🟢 EXCELLENT: Model shows strong knowledge across all areas")
        print("   ✅ Ready for production use")
        print("   ✅ Demonstrates comprehensive learning from training data")
    elif avg_score >= 60:
        print("🟡 GOOD: Model has solid knowledge with some gaps")
        print("   ✅ Suitable for most use cases")
        print("   ⚠️ May need fine-tuning for specific areas")
    elif avg_score >= 40:
        print("🟠 FAIR: Model has basic knowledge but needs improvement")
        print("   ⚠️ Requires additional training or data")
        print("   ⚠️ May give inconsistent responses")
    else:
        print("🔴 POOR: Model needs significant improvement")
        print("   ❌ Not ready for production")
        print("   ❌ Requires retraining with better data or methods")
    
    print(f"\n💡 Recommendations:")
    if avg_score < 60:
        print("   • Consider additional training epochs")
        print("   • Review and improve training data quality")
        print("   • Experiment with different hyperparameters")
    else:
        print("   • Model is performing well!")
        print("   • Consider testing with more diverse questions")
        print("   • Deploy for user testing and feedback")

def main():
    """Main function"""
    print("🎯 Starting Simple Model Test...")
    
    # Check GPU availability
    print(f"🔍 CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    
    # Run test
    success = test_model_simple()
    
    if success:
        print("\n🎉 Testing completed successfully!")
        return 0
    else:
        print("\n❌ Testing failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
