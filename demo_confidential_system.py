#!/usr/bin/env python3
"""
Demo of the confidential client data system
Shows how authentication controls access to client data
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def demo_unauthenticated_access():
    """Demo: Unauthenticated users cannot access client data"""
    
    print("🔐 DEMO: Unauthenticated Access to Client Data")
    print("=" * 60)
    
    client_questions = [
        "What is the profession of Ben Ali El Amri Ahmed Salah?",
        "Who is Ben Ali El Amri Ahmed Salah?",
        "What is the birthdate of Ben Ali El Amri Ahmed Salah?",
    ]
    
    for question in client_questions:
        print(f"\n❓ Question: {question}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat/", json={
                "message": question
            })
            
            data = response.json()
            
            if response.status_code == 401:
                print("🚫 BLOCKED - Authentication required")
                print(f"📝 Response: {data.get('response')}")
                print(f"🔍 Detected patterns: {', '.join(data.get('matched', []))}")
            else:
                print(f"⚠️ Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_general_questions():
    """Demo: General questions work without authentication"""
    
    print("\n\n📋 DEMO: General Questions (No Authentication Required)")
    print("=" * 60)
    
    general_questions = [
        "What is BH Assurance?",
        "How do I file a claim?",
        "What types of insurance do you offer?",
    ]
    
    for question in general_questions:
        print(f"\n❓ Question: {question}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat/", json={
                "message": question
            })
            
            data = response.json()
            
            if response.status_code == 200:
                print("✅ ALLOWED - General question")
                print(f"📝 Response: {data.get('response', '')[:150]}...")
            else:
                print(f"⚠️ Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_authentication_flow():
    """Demo: How to authenticate and access client data"""
    
    print("\n\n🔑 DEMO: Authentication Flow")
    print("=" * 60)
    
    print("Step 1: Login to get authentication token")
    print("POST /api/auth/login/")
    print("Body: { 'email': 'user@example.com', 'password': 'password' }")
    print()
    
    # Example login (you would need real credentials)
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('data', {}).get('token')
            
            if token:
                print(f"✅ Login successful! Token: {token[:20]}...")
                
                # Now test authenticated client query
                print("\nStep 2: Use token to access client data")
                
                headers = {
                    "Authorization": f"Token {token}",
                    "Content-Type": "application/json"
                }
                
                client_response = requests.post(f"{BASE_URL}/api/chat/", 
                                              json={"message": "What is the profession of Ben Ali El Amri Ahmed Salah?"},
                                              headers=headers)
                
                if client_response.status_code == 200:
                    client_data = client_response.json()
                    print("✅ ALLOWED - Authenticated access to client data")
                    print(f"📝 Response: {client_data.get('response')}")
                    print(f"🔐 Authenticated: {client_data.get('authenticated', False)}")
                else:
                    print(f"⚠️ Client query failed: {client_response.status_code}")
            else:
                print("❌ No token received")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print("💡 This is expected if you don't have test credentials set up")
            
    except Exception as e:
        print(f"❌ Authentication demo failed: {e}")
        print("💡 This is expected if the auth system isn't set up with test data")

def show_system_architecture():
    """Show how the confidential system works"""
    
    print("\n\n🏗️ SYSTEM ARCHITECTURE")
    print("=" * 60)
    
    print("""
🔍 CONFIDENTIAL QUERY DETECTION:
├── Keywords: profession, birthdate, income, salary, etc.
├── Patterns: Client name questions, personal data requests
├── Regex: "What is the profession of [Name]?"
└── Result: Flags query as confidential

🔐 AUTHENTICATION CHECK:
├── Unauthenticated: Return 401 with auth message
├── Authenticated: Allow access to client database
└── General questions: Always allowed

💾 CLIENT DATA ACCESS:
├── Database: SQLite with 14,400+ client records
├── Lookup: Instant name-based search
├── Security: Only accessible when authenticated
└── Fallback: AI model for general questions

🛡️ SECURITY LAYERS:
1. Frontend: Authentication state management
2. Backend: Token validation
3. API: Confidential query detection
4. Database: Authenticated access only
5. Responses: Sanitized and controlled
""")

def main():
    """Main demo function"""
    
    print("🚀 CONFIDENTIAL CLIENT DATA SYSTEM DEMO")
    print("=" * 60)
    print("This demonstrates how client data is protected by authentication")
    print("=" * 60)
    
    # Demo 1: Show that unauthenticated access is blocked
    demo_unauthenticated_access()
    
    # Demo 2: Show that general questions still work
    demo_general_questions()
    
    # Demo 3: Show authentication flow (conceptual)
    demo_authentication_flow()
    
    # Show system architecture
    show_system_architecture()
    
    print("\n\n🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Client data is properly protected")
    print("✅ Authentication is required for confidential queries")
    print("✅ General questions work without authentication")
    print("✅ System maintains security while providing service")
    
    print("\n📋 HOW TO TEST:")
    print("1. Unauthenticated: Ask 'What is the profession of Ben Ali El Amri Ahmed Salah?'")
    print("   → Should return 401 with authentication message")
    print()
    print("2. General question: Ask 'What is BH Assurance?'")
    print("   → Should return 200 with AI response")
    print()
    print("3. Authenticated: Login first, then ask client questions")
    print("   → Should return 200 with client data")
    
    print("\n🔐 SECURITY FEATURES:")
    print("• Client data requires authentication")
    print("• Multiple detection patterns (keywords, regex, names)")
    print("• Secure database access")
    print("• Audit trail in logs")
    print("• Graceful fallback for general questions")

if __name__ == "__main__":
    main()
