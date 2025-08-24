#!/usr/bin/env python3
"""
Test script for the authentication API

This script tests all the authentication endpoints to ensure they work correctly.
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:8000/api/auth"

# Test data
TEST_USER_DATA = {
    "email": "test@example.com",
    "name": "Test User",
    "phone_number": "+1234567890",
    "user_type": "CLIENT",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!"
}

LOGIN_DATA = {
    "email": "test@example.com",
    "password": "TestPassword123!"
}

def print_response(response, title):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_user_registration():
    """Test user registration"""
    url = f"{BASE_URL}/register/"
    response = requests.post(url, json=TEST_USER_DATA)
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        data = response.json()
        return data.get('data', {}).get('token')
    return None

def test_user_login():
    """Test user login"""
    url = f"{BASE_URL}/login/"
    response = requests.post(url, json=LOGIN_DATA)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token')
    return None

def test_get_profile(token):
    """Test get user profile"""
    url = f"{BASE_URL}/profile/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Get User Profile")

def test_update_profile(token):
    """Test update user profile"""
    url = f"{BASE_URL}/profile/update/"
    headers = {"Authorization": f"Token {token}"}
    update_data = {
        "name": "Updated Test User",
        "bio": "This is my updated bio"
    }
    response = requests.put(url, json=update_data, headers=headers)
    print_response(response, "Update User Profile")

def test_change_password(token):
    """Test change password"""
    url = f"{BASE_URL}/change-password/"
    headers = {"Authorization": f"Token {token}"}
    password_data = {
        "current_password": "TestPassword123!",
        "new_password": "NewPassword123!",
        "new_password_confirm": "NewPassword123!"
    }
    response = requests.post(url, json=password_data, headers=headers)
    print_response(response, "Change Password")

def test_get_sessions(token):
    """Test get user sessions"""
    url = f"{BASE_URL}/sessions/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Get User Sessions")

def test_password_reset_request():
    """Test password reset request"""
    url = f"{BASE_URL}/request-password-reset/"
    reset_data = {"email": "test@example.com"}
    response = requests.post(url, json=reset_data)
    print_response(response, "Password Reset Request")

def test_logout(token):
    """Test user logout"""
    url = f"{BASE_URL}/logout/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(url, headers=headers)
    print_response(response, "User Logout")

def test_invalid_registration():
    """Test invalid registration data"""
    url = f"{BASE_URL}/register/"
    invalid_data = {
        "email": "invalid-email",
        "name": "",
        "password": "123",
        "password_confirm": "456"
    }
    response = requests.post(url, json=invalid_data)
    print_response(response, "Invalid Registration (Should Fail)")

def test_invalid_login():
    """Test invalid login"""
    url = f"{BASE_URL}/login/"
    invalid_login = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    response = requests.post(url, json=invalid_login)
    print_response(response, "Invalid Login (Should Fail)")

def main():
    """Run all authentication tests"""
    print("🚀 Starting Authentication API Tests")
    print("Make sure your Django server is running on http://localhost:8000")
    
    # Test invalid cases first
    test_invalid_registration()
    test_invalid_login()
    
    # Test user registration
    token = test_user_registration()
    if not token:
        print("❌ Registration failed, stopping tests")
        return
    
    # Test profile operations
    test_get_profile(token)
    test_update_profile(token)
    test_get_sessions(token)
    
    # Test password operations
    test_password_reset_request()
    # Note: Don't test change_password as it would invalidate the token
    
    # Test logout
    test_logout(token)
    
    # Test login after registration
    login_token = test_user_login()
    if login_token:
        test_get_profile(login_token)
        test_logout(login_token)
    
    print(f"\n{'='*50}")
    print("🎉 Authentication API Tests Completed!")
    print("Check the responses above to verify everything works correctly.")
    print(f"{'='*50}")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure your Django server is running:")
        print("python manage.py runserver")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(0)
