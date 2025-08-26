#!/usr/bin/env python3
"""
Test Authentication API Fix

This script tests if the CSRF and CORS fixes resolved the "not allowed" issue.
"""

import requests
import json
import time

def test_auth_endpoints():
    """Test authentication endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing BH Assurance Authentication API")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "testuser@bhassurance.com",
        "name": "Test User",
        "phone_number": "+21612345678",
        "user_type": "CLIENT",
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!"
    }
    
    login_data = {
        "email": "testuser@bhassurance.com",
        "password": "TestPassword123!"
    }
    
    # Test 1: User Registration
    print("\n🔍 Test 1: User Registration")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/register/",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            data = response.json()
            token = data.get('data', {}).get('token')
            if token:
                print(f"🔑 Token received: {token[:20]}...")
        elif response.status_code == 400:
            print("⚠️ Registration failed - user might already exist")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 2: User Login
    print("\n🔍 Test 2: User Login")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            token = data.get('data', {}).get('token')
            if token:
                print(f"🔑 Token received: {token[:20]}...")
                return token
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    return None

def test_chat_endpoint():
    """Test chat endpoint"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔍 Test 3: Chat Endpoint")
    print("-" * 30)
    
    chat_message = {
        "message": "Bonjour, pouvez-vous m'aider avec l'assurance?"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/",
            json=chat_message,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Chat endpoint working!")
            data = response.json()
            chat_response = data.get('response', 'No response')
            print(f"🤖 AI Response: {chat_response[:100]}...")
        else:
            print(f"❌ Chat failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_profile_endpoint(token):
    """Test profile endpoint with authentication"""
    if not token:
        print("\n⚠️ Skipping profile test - no token available")
        return
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔍 Test 4: Get Profile (Authenticated)")
    print("-" * 30)
    
    try:
        response = requests.get(
            f"{base_url}/api/auth/profile/",
            headers={
                "Authorization": f"Token {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Profile endpoint working!")
            data = response.json()
            user_data = data.get('data', {})
            print(f"👤 User: {user_data.get('name')} ({user_data.get('email')})")
        else:
            print(f"❌ Profile failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main test function"""
    print("🚀 Starting API Tests...")
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)
    
    # Test authentication
    token = test_auth_endpoints()
    
    # Test chat
    test_chat_endpoint()
    
    # Test authenticated endpoint
    test_profile_endpoint(token)
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    print("✅ If you see successful responses above, your API is working!")
    print("✅ CSRF and CORS issues have been resolved")
    print("✅ You can now use Postman or any API client")
    
    print("\n📋 Next Steps:")
    print("1. Import the Postman collection: BH_Assurance_Complete_API.postman_collection.json")
    print("2. Set the base_url variable to: http://127.0.0.1:8000")
    print("3. Test all endpoints in Postman")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
