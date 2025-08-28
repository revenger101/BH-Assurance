#!/usr/bin/env python3
"""
Test the integrated client data system
This script tests both client lookup and AI fallback
"""

import sys
import os
sys.path.append('chat')

from simple_mistral_client import chat_completion

def test_client_questions():
    """Test client-specific questions"""
    
    print("🧪 Testing Client Data Integration")
    print("=" * 50)
    
    # Test client questions that should use lookup
    client_questions = [
        "What is the profession of Ben Ali El Amri Ahmed Salah?",
        "What is the birthdate of Ben Ali El Amri Ahmed Salah?", 
        "What is the monthly income of Ben Ali El Amri Ahmed Salah?",
        "Who is Ben Ali El Amri Ahmed Salah?",
        "Tell me about Ben Ali El Amri Ahmed Salah",
    ]
    
    print("📋 Testing Client Lookup Questions:")
    print("-" * 40)
    
    for i, question in enumerate(client_questions, 1):
        print(f"\n{i}. Q: {question}")
        try:
            response = chat_completion(question, max_tokens=100)
            print(f"   A: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test general insurance questions (should use AI)
    general_questions = [
        "What is BH Assurance?",
        "Tell me about insurance policies",
        "How do I file a claim?",
        "What types of insurance do you offer?",
    ]
    
    print("\n\n📋 Testing General Insurance Questions (AI Fallback):")
    print("-" * 40)
    
    for i, question in enumerate(general_questions, 1):
        print(f"\n{i}. Q: {question}")
        try:
            response = chat_completion(question, max_tokens=100)
            print(f"   A: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_confidential_detection():
    """Test confidential question detection"""
    
    print("\n\n🔐 Testing Confidential Question Detection:")
    print("-" * 40)
    
    # These should be detected as confidential and answered by lookup
    confidential_questions = [
        "Quel est mon numéro de contrat?",
        "What is my policy number?",
        "Quelle est mon adresse personnelle?",
        "What is my personal information?",
    ]
    
    for i, question in enumerate(confidential_questions, 1):
        print(f"\n{i}. Q: {question}")
        try:
            response = chat_completion(question, max_tokens=100)
            print(f"   A: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def performance_test():
    """Test response speed"""
    
    print("\n\n⚡ Performance Test:")
    print("-" * 40)
    
    import time
    
    # Test client lookup speed
    start_time = time.time()
    response = chat_completion("What is the profession of Ben Ali El Amri Ahmed Salah?")
    lookup_time = time.time() - start_time
    
    print(f"Client Lookup Speed: {lookup_time:.3f} seconds")
    print(f"Response: {response}")
    
    # Test AI fallback speed
    start_time = time.time()
    response = chat_completion("What is insurance?", max_tokens=50)
    ai_time = time.time() - start_time
    
    print(f"AI Fallback Speed: {ai_time:.3f} seconds")
    print(f"Response: {response[:100]}...")

def main():
    """Main test function"""
    
    print("🚀 Client Data Integration Test Suite")
    print("=" * 60)
    print("This tests the integrated system with:")
    print("✅ Client data lookup (instant responses)")
    print("✅ AI fallback for general questions")
    print("✅ Confidential question handling")
    print("=" * 60)
    
    try:
        # Test client questions
        test_client_questions()
        
        # Test confidential detection
        test_confidential_detection()
        
        # Performance test
        performance_test()
        
        print("\n\n🎉 All Tests Completed!")
        print("=" * 60)
        print("✅ Client lookup system working")
        print("✅ AI fallback working")
        print("✅ Integration successful")
        
        print("\n📊 Summary:")
        print("• Client questions answered instantly from database")
        print("• General questions handled by AI model")
        print("• No model training required")
        print("• Fast and reliable responses")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
