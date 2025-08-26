#!/usr/bin/env python3
"""
Quick API Test Script

Tests a few key questions to evaluate model performance through the API.
"""

import requests
import json
import time

def test_single_question(question, expected_keywords=None):
    """Test a single question"""
    print(f"\n🔍 Testing: {question}")
    print("-" * 50)
    
    try:
        # Send request
        url = "http://127.0.0.1:8000/api/chat/"
        payload = {"message": question}
        headers = {"Content-Type": "application/json"}
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "No response")
            
            print(f"✅ Response ({response_time:.2f}s):")
            print(f"   {answer}")
            
            # Simple evaluation
            score = 0
            feedback = []
            
            if len(answer) > 10:
                score += 30
                feedback.append("Good length")
            
            if expected_keywords:
                found = sum(1 for kw in expected_keywords if kw.lower() in answer.lower())
                keyword_score = (found / len(expected_keywords)) * 50
                score += keyword_score
                feedback.append(f"Keywords: {found}/{len(expected_keywords)}")
            
            # Check for French and insurance terms
            insurance_terms = ["assurance", "garantie", "société", "produit", "branche"]
            found_terms = sum(1 for term in insurance_terms if term in answer.lower())
            if found_terms > 0:
                score += 20
                feedback.append(f"Insurance terms: {found_terms}")
            
            print(f"📊 Score: {score:.0f}/100")
            print(f"💡 Feedback: {', '.join(feedback)}")
            
            return True, answer, score
            
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False, f"API Error: {response.status_code}", 0
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False, f"Request Error: {str(e)}", 0

def main():
    """Main testing function"""
    print("🚀 Quick API Model Test")
    print("=" * 50)
    
    # Test questions covering different categories
    test_questions = [
        {
            "question": "Quelle est l'activité de la société Societe_000001?",
            "keywords": ["société", "activité", "secteur"],
            "category": "Company Data"
        },
        {
            "question": "Quels sont les profils cibles pour le produit TEMPORAIRE DECES?",
            "keywords": ["profils", "cibles", "emprunteurs", "famille"],
            "category": "Product Mapping"
        },
        {
            "question": "Que couvre la garantie DECES?",
            "keywords": ["garantie", "couvre", "deces"],
            "category": "Guarantees"
        },
        {
            "question": "Quels sont les différents types d'assurance vie?",
            "keywords": ["types", "assurance", "vie"],
            "category": "General Knowledge"
        },
        {
            "question": "Bonjour, comment allez-vous?",
            "keywords": [],
            "category": "Greeting Test"
        }
    ]
    
    results = []
    successful_tests = 0
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"📝 Test {i}/5: {test['category']}")
        print(f"{'='*60}")
        
        success, response, score = test_single_question(
            test["question"], 
            test.get("keywords")
        )
        
        if success:
            successful_tests += 1
        
        results.append({
            "question": test["question"],
            "category": test["category"],
            "success": success,
            "response": response,
            "score": score
        })
        
        # Small delay between requests
        time.sleep(3)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    print(f"📈 Total Tests: {len(test_questions)}")
    print(f"✅ Successful Tests: {successful_tests}/{len(test_questions)}")
    
    if successful_tests > 0:
        successful_results = [r for r in results if r["success"]]
        avg_score = sum(r["score"] for r in successful_results) / len(successful_results)
        
        print(f"📊 Average Score: {avg_score:.1f}/100")
        
        # Performance assessment
        if avg_score >= 80:
            print("🟢 EXCELLENT: Model shows strong performance!")
        elif avg_score >= 60:
            print("🟡 GOOD: Model performs well with some areas for improvement")
        elif avg_score >= 40:
            print("🟠 FAIR: Model has basic knowledge but needs enhancement")
        else:
            print("🔴 POOR: Model needs significant improvement")
        
        print(f"\n📋 Individual Results:")
        for result in results:
            status = "✅" if result["success"] else "❌"
            score_text = f"({result['score']:.0f}/100)" if result["success"] else "(Failed)"
            print(f"   {status} {result['category']}: {score_text}")
    
    else:
        print("❌ No successful tests - API may not be working properly")
    
    print(f"\n🎯 Model Assessment:")
    if successful_tests >= 4:
        print("✅ Your BH Insurance model is working and responding to questions!")
        print("✅ The model has learned from your training data")
        print("✅ Ready for further testing and deployment")
    elif successful_tests >= 2:
        print("⚠️ Model is partially working - some responses successful")
        print("⚠️ May need debugging or additional training")
    else:
        print("❌ Model appears to have issues - API not responding properly")
        print("❌ Check server logs and model loading")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
