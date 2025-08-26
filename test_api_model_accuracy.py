#!/usr/bin/env python3
"""
API Model Accuracy Testing Script

Tests the trained model through the Django REST API to evaluate
its performance on various insurance-related questions.
"""

import requests
import json
import time
from datetime import datetime

class APIModelTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/api/chat/"
        self.test_results = []
        
    def test_api_connection(self):
        """Test if the API is accessible"""
        try:
            response = requests.get(self.base_url, timeout=10)
            print(f"✅ API connection successful (Status: {response.status_code})")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    def send_chat_message(self, message):
        """Send a message to the chat API"""
        try:
            payload = {"message": message}
            headers = {"Content-Type": "application/json"}
            
            start_time = time.time()
            response = requests.post(
                self.chat_endpoint, 
                json=payload, 
                headers=headers,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response"), response_time, True
            else:
                return f"API Error: {response.status_code} - {response.text}", response_time, False
                
        except requests.exceptions.RequestException as e:
            return f"Request Error: {str(e)}", 0, False
    
    def evaluate_response_quality(self, question, response, expected_keywords=None, category="General"):
        """Evaluate the quality of a response"""
        score = 0
        feedback = []
        
        # Basic response checks
        if "Error" in response:
            feedback.append("API or generation error")
            return 0, feedback
        
        if len(response.strip()) < 10:
            feedback.append("Response too short")
            return 10, feedback
        
        # Length and coherence (30 points)
        if len(response.split()) >= 5:
            score += 15
            feedback.append("Adequate response length")
        
        if len(response.split()) >= 10:
            score += 15
            feedback.append("Good response length")
        
        # Keyword relevance (40 points)
        if expected_keywords:
            found_keywords = 0
            for keyword in expected_keywords:
                if keyword.lower() in response.lower():
                    found_keywords += 1
            
            keyword_score = (found_keywords / len(expected_keywords)) * 40
            score += keyword_score
            feedback.append(f"Found {found_keywords}/{len(expected_keywords)} expected keywords")
        else:
            # If no keywords provided, check for question relevance
            question_words = set(question.lower().split())
            response_words = set(response.lower().split())
            common_words = question_words.intersection(response_words)
            
            if len(common_words) >= 2:
                score += 30
                feedback.append("Response appears relevant to question")
        
        # Language and domain appropriateness (30 points)
        insurance_terms = [
            "assurance", "garantie", "police", "prime", "sinistre", "couverture",
            "bénéficiaire", "souscripteur", "indemnité", "franchise", "risque",
            "société", "entreprise", "produit", "branche", "vie", "deces"
        ]
        
        found_insurance_terms = sum(1 for term in insurance_terms if term in response.lower())
        if found_insurance_terms >= 1:
            score += 15
            feedback.append(f"Uses appropriate insurance terminology ({found_insurance_terms} terms)")
        
        # French language check
        french_indicators = ["le", "la", "les", "de", "du", "des", "pour", "dans", "avec", "est", "sont"]
        french_score = sum(1 for word in french_indicators if word in response.lower())
        if french_score >= 2:
            score += 15
            feedback.append("Responds in French")
        
        return min(score, 100), feedback
    
    def run_comprehensive_test(self):
        """Run comprehensive testing of the model"""
        print("🚀 Starting Comprehensive API Model Testing")
        print("=" * 60)
        
        if not self.test_api_connection():
            return False
        
        # Test categories
        test_categories = [
            self.test_company_data(),
            self.test_product_mapping(),
            self.test_guarantees(),
            self.test_pdf_documents(),
            self.test_general_insurance(),
            self.test_edge_cases()
        ]
        
        # Calculate and display results
        self.display_results()
        return True
    
    def test_company_data(self):
        """Test company data knowledge"""
        print("\n🏢 Testing Company Data Knowledge")
        print("-" * 40)
        
        questions = [
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
                "category": "Company Fiscal"
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
        
        return self.run_test_batch(questions, "Company Data")
    
    def test_product_mapping(self):
        """Test product mapping knowledge"""
        print("\n🎯 Testing Product Mapping Knowledge")
        print("-" * 40)
        
        questions = [
            {
                "question": "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
                "keywords": ["profils", "cibles", "temporaire", "deces", "emprunteurs"],
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
                "keywords": ["acheter", "homme", "clef", "entreprise"],
                "category": "Product Recommendation"
            },
            {
                "question": "Quels produits sont recommandés pour les entreprises?",
                "keywords": ["produits", "entreprises", "recommandés"],
                "category": "Business Products"
            }
        ]
        
        return self.run_test_batch(questions, "Product Mapping")
    
    def test_guarantees(self):
        """Test guarantee knowledge"""
        print("\n🛡️ Testing Guarantee Knowledge")
        print("-" * 40)
        
        questions = [
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
            }
        ]
        
        return self.run_test_batch(questions, "Guarantees")
    
    def test_pdf_documents(self):
        """Test PDF document knowledge"""
        print("\n📄 Testing PDF Document Knowledge")
        print("-" * 40)
        
        questions = [
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
            }
        ]
        
        return self.run_test_batch(questions, "PDF Documents")
    
    def test_general_insurance(self):
        """Test general insurance knowledge"""
        print("\n🏢 Testing General Insurance Knowledge")
        print("-" * 40)
        
        questions = [
            {
                "question": "Quels sont les différents types d'assurance vie disponibles?",
                "keywords": ["types", "assurance", "vie"],
                "category": "Life Insurance Types"
            },
            {
                "question": "Comment choisir une assurance pour une entreprise?",
                "keywords": ["choisir", "assurance", "entreprise"],
                "category": "Business Insurance"
            },
            {
                "question": "Quelles garanties sont importantes pour un emprunteur?",
                "keywords": ["garanties", "emprunteur"],
                "category": "Borrower Insurance"
            }
        ]
        
        return self.run_test_batch(questions, "General Insurance")
    
    def test_edge_cases(self):
        """Test edge cases"""
        print("\n⚠️ Testing Edge Cases")
        print("-" * 40)
        
        questions = [
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
                "question": "Bonjour comment allez-vous?",
                "keywords": [],
                "category": "Irrelevant Question"
            }
        ]
        
        return self.run_test_batch(questions, "Edge Cases")
    
    def run_test_batch(self, questions, category_name):
        """Run a batch of test questions"""
        category_results = []
        
        for i, test_case in enumerate(questions, 1):
            question = test_case["question"]
            expected_keywords = test_case.get("keywords", [])
            subcategory = test_case.get("category", "Unknown")
            
            print(f"\n🔍 Test {i}: {subcategory}")
            print(f"Question: {question}")
            
            # Send question to API
            response, response_time, success = self.send_chat_message(question)
            print(f"Response: {response}")
            print(f"Time: {response_time:.2f}s")
            
            if success:
                # Evaluate response
                score, feedback = self.evaluate_response_quality(
                    question, response, expected_keywords, category_name
                )
                print(f"Score: {score}/100")
                print(f"Feedback: {', '.join(feedback)}")
            else:
                score = 0
                feedback = ["API request failed"]
                print(f"Score: {score}/100 (API Error)")
            
            # Store result
            result = {
                "category": category_name,
                "subcategory": subcategory,
                "question": question,
                "response": response,
                "score": score,
                "response_time": response_time,
                "success": success,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            category_results.append(result)
            self.test_results.append(result)
            
            # Small delay between requests
            time.sleep(2)
        
        # Category summary
        if category_results:
            successful_tests = [r for r in category_results if r["success"]]
            if successful_tests:
                avg_score = sum(r["score"] for r in successful_tests) / len(successful_tests)
                avg_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
                print(f"\n📊 {category_name} Results:")
                print(f"   Average Score: {avg_score:.1f}/100")
                print(f"   Average Time: {avg_time:.2f}s")
                print(f"   Success Rate: {len(successful_tests)}/{len(category_results)}")
        
        return category_results
    
    def display_results(self):
        """Display comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        if not self.test_results:
            print("❌ No test results available")
            return
        
        # Filter successful tests
        successful_tests = [r for r in self.test_results if r["success"]]
        total_tests = len(self.test_results)
        success_rate = len(successful_tests) / total_tests * 100
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Successful Tests: {len(successful_tests)} ({success_rate:.1f}%)")
        
        if not successful_tests:
            print("❌ No successful tests to analyze")
            return
        
        # Overall statistics
        avg_score = sum(r["score"] for r in successful_tests) / len(successful_tests)
        avg_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
        
        print(f"📊 Average Score: {avg_score:.1f}/100")
        print(f"⏱️ Average Response Time: {avg_time:.2f}s")
        
        # Score distribution
        excellent = sum(1 for r in successful_tests if r["score"] >= 80)
        good = sum(1 for r in successful_tests if 60 <= r["score"] < 80)
        fair = sum(1 for r in successful_tests if 40 <= r["score"] < 60)
        poor = sum(1 for r in successful_tests if r["score"] < 40)
        
        print(f"\n📊 Performance Distribution:")
        print(f"🟢 Excellent (80-100): {excellent} ({excellent/len(successful_tests)*100:.1f}%)")
        print(f"🟡 Good (60-79): {good} ({good/len(successful_tests)*100:.1f}%)")
        print(f"🟠 Fair (40-59): {fair} ({fair/len(successful_tests)*100:.1f}%)")
        print(f"🔴 Poor (0-39): {poor} ({poor/len(successful_tests)*100:.1f}%)")
        
        # Category performance
        categories = {}
        for result in successful_tests:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result["score"])
        
        print(f"\n📊 Category Performance:")
        for category, scores in categories.items():
            avg_cat_score = sum(scores) / len(scores)
            print(f"   {category}: {avg_cat_score:.1f}/100 ({len(scores)} tests)")
        
        # Overall assessment
        print(f"\n🎯 OVERALL MODEL ASSESSMENT:")
        if avg_score >= 80:
            print("🟢 EXCELLENT: Model demonstrates strong knowledge and accuracy")
            print("   ✅ Ready for production deployment")
            print("   ✅ Comprehensive understanding of insurance domain")
        elif avg_score >= 60:
            print("🟡 GOOD: Model shows solid performance with room for improvement")
            print("   ✅ Suitable for most use cases")
            print("   ⚠️ Consider additional training for specific weak areas")
        elif avg_score >= 40:
            print("🟠 FAIR: Model has basic knowledge but needs enhancement")
            print("   ⚠️ Requires additional training data or fine-tuning")
            print("   ⚠️ May provide inconsistent responses")
        else:
            print("🔴 POOR: Model needs significant improvement")
            print("   ❌ Not ready for production use")
            print("   ❌ Requires comprehensive retraining")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_model_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main testing function"""
    print("🚀 BH Insurance API Model Testing")
    print("=" * 50)
    
    # Initialize tester
    tester = APIModelTester()
    
    # Run comprehensive test
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 API testing completed successfully!")
    else:
        print("\n❌ API testing failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
