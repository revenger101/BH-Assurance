#!/usr/bin/env python3
"""
Comprehensive Model Accuracy Testing for BH Insurance

This script tests the trained model's accuracy and knowledge across all data sources:
1. Insurance company data (Excel)
2. Insurance documents (PDF)
3. Product mapping and guarantees (New Excel files)

Tests various question types and evaluates response quality.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import os
import time
import random
from datetime import datetime

class ModelTester:
    def __init__(self, model_path="bhagent/outputs/sft_mistral_combined/checkpoint-882"):
        self.model_path = model_path
        self.base_model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        self.model = None
        self.tokenizer = None
        self.test_results = []
        
    def load_model(self):
        """Load the trained model"""
        print("🔄 Loading trained model...")
        print(f"Model path: {self.model_path}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model
            print("Loading base model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                offload_folder="bhagent/outputs/offload"
            )
            
            # Load trained adapters
            print("Loading trained adapters...")
            self.model = PeftModel.from_pretrained(self.model, self.model_path)
            self.model.eval()
            
            print("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def generate_response(self, prompt, max_length=512, temperature=0.7):
        """Generate response from the model"""
        try:
            # Format prompt
            formatted_prompt = prompt + "\n\n###\n\n"
            
            # Tokenize
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            
            # Generate
            start_time = time.time()
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            generation_time = time.time() - start_time
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract completion part
            if "###" in response:
                response = response.split("###")[-1].strip()
            
            # Remove END token
            if response.endswith(" END"):
                response = response[:-4].strip()
            
            return response, generation_time
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Error: {str(e)}", 0
    
    def evaluate_response_quality(self, question, response, expected_keywords=None):
        """Evaluate the quality of a response"""
        score = 0
        feedback = []
        
        # Basic checks
        if len(response) < 10:
            feedback.append("Response too short")
        else:
            score += 20
        
        if "Error:" in response:
            feedback.append("Generation error occurred")
            return score, feedback
        
        # Check for relevant keywords if provided
        if expected_keywords:
            found_keywords = 0
            for keyword in expected_keywords:
                if keyword.lower() in response.lower():
                    found_keywords += 1
            
            keyword_score = (found_keywords / len(expected_keywords)) * 40
            score += keyword_score
            feedback.append(f"Found {found_keywords}/{len(expected_keywords)} expected keywords")
        
        # Check for coherence (basic)
        if len(response.split()) > 5:
            score += 20
            feedback.append("Response has good length")
        
        # Check if response seems relevant to question
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        common_words = question_words.intersection(response_words)
        
        if len(common_words) > 2:
            score += 20
            feedback.append("Response seems relevant to question")
        
        return min(score, 100), feedback
    
    def run_comprehensive_test(self):
        """Run comprehensive testing across all data types"""
        print("🧪 Starting Comprehensive Model Testing")
        print("=" * 60)
        
        if not self.load_model():
            return False
        
        # Test categories
        test_categories = [
            self.test_company_data(),
            self.test_product_mapping(),
            self.test_guarantees(),
            self.test_pdf_documents(),
            self.test_general_insurance_knowledge(),
            self.test_edge_cases()
        ]
        
        # Calculate overall results
        self.calculate_overall_results()
        
        return True
    
    def test_company_data(self):
        """Test knowledge of insurance company data"""
        print("\n📊 Testing Company Data Knowledge")
        print("-" * 40)
        
        company_questions = [
            {
                "question": "Quelle est l'activité de la société Societe_000001?",
                "keywords": ["société", "activité", "secteur"],
                "category": "Company Activity"
            },
            {
                "question": "Où se trouve la société Societe_000002?",
                "keywords": ["société", "trouve", "ville", "gouvernorat"],
                "category": "Company Location"
            },
            {
                "question": "Quel est le matricule fiscal de Societe_000003?",
                "keywords": ["matricule", "fiscal"],
                "category": "Company Fiscal Info"
            },
            {
                "question": "Quelles sont les entreprises dans le secteur SERVICES PERSONNELS?",
                "keywords": ["entreprises", "secteur", "services"],
                "category": "Sector Query"
            },
            {
                "question": "Listez les sociétés à TUNIS",
                "keywords": ["sociétés", "tunis"],
                "category": "Location Query"
            }
        ]
        
        return self.run_test_batch(company_questions, "Company Data")
    
    def test_product_mapping(self):
        """Test knowledge of product mapping data"""
        print("\n🎯 Testing Product Mapping Knowledge")
        print("-" * 40)
        
        product_questions = [
            {
                "question": "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
                "keywords": ["profils", "cibles", "temporaire", "deces"],
                "category": "Target Profiles"
            },
            {
                "question": "À quelle branche appartient le produit ASSURANCE MIXTE VIE?",
                "keywords": ["branche", "assurance", "mixte", "vie"],
                "category": "Product Branch"
            },
            {
                "question": "Quels sont les produits disponibles dans la branche VIE?",
                "keywords": ["produits", "branche", "vie"],
                "category": "Branch Products"
            },
            {
                "question": "Qui devrait acheter le produit ASSURANCE HOMME CLEF?",
                "keywords": ["acheter", "homme", "clef"],
                "category": "Product Recommendation"
            },
            {
                "question": "Quels produits sont recommandés pour les entreprises?",
                "keywords": ["produits", "entreprises", "recommandés"],
                "category": "Business Products"
            }
        ]
        
        return self.run_test_batch(product_questions, "Product Mapping")
    
    def test_guarantees(self):
        """Test knowledge of guarantee descriptions"""
        print("\n🛡️ Testing Guarantee Knowledge")
        print("-" * 40)
        
        guarantee_questions = [
            {
                "question": "Que couvre la garantie DECES?",
                "keywords": ["couvre", "garantie", "deces"],
                "category": "Guarantee Coverage"
            },
            {
                "question": "Quelles sont les garanties disponibles pour le produit TEMPORAIRE DECES?",
                "keywords": ["garanties", "disponibles", "temporaire"],
                "category": "Product Guarantees"
            },
            {
                "question": "Pouvez-vous expliquer la garantie INVALIDITE PERMANENTE TOTALE?",
                "keywords": ["garantie", "invalidite", "permanente"],
                "category": "Guarantee Explanation"
            },
            {
                "question": "Quel produit offre la garantie INCAPACITE TEMPORAIRE DE TRAVAIL?",
                "keywords": ["produit", "incapacite", "travail"],
                "category": "Guarantee Product"
            },
            {
                "question": "Quelles sont les principales garanties en assurance vie?",
                "keywords": ["garanties", "assurance", "vie"],
                "category": "Life Insurance Guarantees"
            }
        ]
        
        return self.run_test_batch(guarantee_questions, "Guarantees")
    
    def test_pdf_documents(self):
        """Test knowledge from PDF documents"""
        print("\n📄 Testing PDF Document Knowledge")
        print("-" * 40)
        
        pdf_questions = [
            {
                "question": "Que contient le document ASSURANCE BRIS DE GLACES?",
                "keywords": ["document", "bris", "glaces"],
                "category": "Document Content"
            },
            {
                "question": "Quelles sont les conditions générales pour MULTIRISQUE HABITATION?",
                "keywords": ["conditions", "multirisque", "habitation"],
                "category": "General Conditions"
            },
            {
                "question": "Expliquez les conditions de l'assurance automobile",
                "keywords": ["conditions", "assurance", "automobile"],
                "category": "Auto Insurance"
            },
            {
                "question": "Quelles sont les exclusions dans l'assurance habitation?",
                "keywords": ["exclusions", "assurance", "habitation"],
                "category": "Insurance Exclusions"
            }
        ]
        
        return self.run_test_batch(pdf_questions, "PDF Documents")
    
    def test_general_insurance_knowledge(self):
        """Test general insurance knowledge"""
        print("\n🏢 Testing General Insurance Knowledge")
        print("-" * 40)
        
        general_questions = [
            {
                "question": "Quels sont les différents types d'assurance vie disponibles?",
                "keywords": ["types", "assurance", "vie"],
                "category": "Life Insurance Types"
            },
            {
                "question": "Comment choisir une assurance pour une entreprise?",
                "keywords": ["choisir", "assurance", "entreprise"],
                "category": "Business Insurance Selection"
            },
            {
                "question": "Quelles garanties sont importantes pour un emprunteur?",
                "keywords": ["garanties", "emprunteur"],
                "category": "Borrower Insurance"
            },
            {
                "question": "Quelle est la différence entre assurance vie et assurance décès?",
                "keywords": ["différence", "vie", "décès"],
                "category": "Insurance Comparison"
            }
        ]
        
        return self.run_test_batch(general_questions, "General Knowledge")
    
    def test_edge_cases(self):
        """Test edge cases and model robustness"""
        print("\n⚠️ Testing Edge Cases")
        print("-" * 40)
        
        edge_questions = [
            {
                "question": "Société inexistante XYZ123?",
                "keywords": [],
                "category": "Non-existent Company"
            },
            {
                "question": "Produit SUPER_ASSURANCE_MAGIQUE?",
                "keywords": [],
                "category": "Non-existent Product"
            },
            {
                "question": "",
                "keywords": [],
                "category": "Empty Question"
            },
            {
                "question": "Bonjour comment allez-vous?",
                "keywords": [],
                "category": "Irrelevant Question"
            }
        ]
        
        return self.run_test_batch(edge_questions, "Edge Cases")
    
    def run_test_batch(self, questions, category_name):
        """Run a batch of test questions"""
        category_results = []
        
        for i, test_case in enumerate(questions, 1):
            question = test_case["question"]
            expected_keywords = test_case.get("keywords", [])
            subcategory = test_case.get("category", "Unknown")
            
            print(f"\n🔍 Test {i}: {subcategory}")
            print(f"Question: {question}")
            
            if not question.strip():
                print("⚠️ Empty question, skipping...")
                continue
            
            # Generate response
            response, gen_time = self.generate_response(question)
            print(f"Response: {response}")
            print(f"Generation time: {gen_time:.2f}s")
            
            # Evaluate response
            score, feedback = self.evaluate_response_quality(question, response, expected_keywords)
            print(f"Score: {score}/100")
            print(f"Feedback: {', '.join(feedback)}")
            
            # Store result
            result = {
                "category": category_name,
                "subcategory": subcategory,
                "question": question,
                "response": response,
                "score": score,
                "generation_time": gen_time,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            category_results.append(result)
            self.test_results.append(result)
            
            # Small delay to prevent overheating
            time.sleep(1)
        
        # Calculate category average
        if category_results:
            avg_score = sum(r["score"] for r in category_results) / len(category_results)
            print(f"\n📊 {category_name} Average Score: {avg_score:.1f}/100")
        
        return category_results
    
    def calculate_overall_results(self):
        """Calculate and display overall test results"""
        print("\n" + "=" * 60)
        print("📈 OVERALL TEST RESULTS")
        print("=" * 60)
        
        if not self.test_results:
            print("❌ No test results available")
            return
        
        # Overall statistics
        total_tests = len(self.test_results)
        avg_score = sum(r["score"] for r in self.test_results) / total_tests
        avg_time = sum(r["generation_time"] for r in self.test_results) / total_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"📊 Average Score: {avg_score:.1f}/100")
        print(f"⏱️ Average Generation Time: {avg_time:.2f}s")
        
        # Score distribution
        excellent = sum(1 for r in self.test_results if r["score"] >= 80)
        good = sum(1 for r in self.test_results if 60 <= r["score"] < 80)
        fair = sum(1 for r in self.test_results if 40 <= r["score"] < 60)
        poor = sum(1 for r in self.test_results if r["score"] < 40)
        
        print(f"\n📊 Score Distribution:")
        print(f"   🟢 Excellent (80-100): {excellent} ({excellent/total_tests*100:.1f}%)")
        print(f"   🟡 Good (60-79): {good} ({good/total_tests*100:.1f}%)")
        print(f"   🟠 Fair (40-59): {fair} ({fair/total_tests*100:.1f}%)")
        print(f"   🔴 Poor (0-39): {poor} ({poor/total_tests*100:.1f}%)")
        
        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result["score"])
        
        print(f"\n📊 Category Performance:")
        for category, scores in categories.items():
            avg_cat_score = sum(scores) / len(scores)
            print(f"   {category}: {avg_cat_score:.1f}/100 ({len(scores)} tests)")
        
        # Save results to file
        self.save_results()
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if avg_score >= 80:
            print("🟢 EXCELLENT: Model shows strong knowledge across all areas")
        elif avg_score >= 60:
            print("🟡 GOOD: Model has solid knowledge with some gaps")
        elif avg_score >= 40:
            print("🟠 FAIR: Model has basic knowledge but needs improvement")
        else:
            print("🔴 POOR: Model needs significant improvement")
    
    def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bhagent/model_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {filename}")

def main():
    """Main testing function"""
    print("🚀 BH Insurance Model Accuracy Testing")
    print("=" * 60)
    
    # Initialize tester
    tester = ModelTester()
    
    # Run comprehensive test
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Testing completed successfully!")
    else:
        print("\n❌ Testing failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
