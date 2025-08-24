#!/usr/bin/env python3
"""
Setup script for BH Assurance Authentication System

This script sets up the authentication system by:
1. Running migrations
2. Creating a superuser
3. Testing the API endpoints
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhagent.settings')

def run_command(command, description):
    """Run a shell command and print the result"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print("Output:", result.stdout)
        else:
            print(f"❌ {description} failed!")
            if result.stderr:
                print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def setup_authentication():
    """Setup the authentication system"""
    print("🚀 Setting up BH Assurance Authentication System")
    print("=" * 60)
    
    # Step 1: Install required packages
    print("\n📦 Installing required packages...")
    packages = [
        "psycopg2-binary",
        "djangorestframework",
        "django-cors-headers"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing...")
    
    # Step 2: Make migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("⚠️ Migration creation failed, but continuing...")
    
    # Step 3: Run migrations
    if not run_command("python manage.py migrate", "Running migrations"):
        print("❌ Migration failed! Please check your database configuration.")
        return False
    
    # Step 4: Collect static files (if needed)
    # run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("\n✅ Authentication system setup completed!")
    
    # Step 5: Show next steps
    print("\n📋 Next Steps:")
    print("1. Create a superuser:")
    print("   python manage.py createsuperuser")
    print("\n2. Start the development server:")
    print("   python manage.py runserver")
    print("\n3. Test the API endpoints:")
    print("   python test_auth_api.py")
    print("\n4. Import the Postman collection:")
    print("   BH_Assurance_Auth_API.postman_collection.json")
    
    return True

def create_test_data():
    """Create test data for the authentication system"""
    print("\n🧪 Creating test data...")
    
    try:
        # Setup Django
        django.setup()
        
        from authentication.models import CustomUser
        from django.contrib.auth.hashers import make_password
        
        # Create test users
        test_users = [
            {
                'email': 'client@bhassurance.com',
                'name': 'Test Client',
                'phone_number': '+21612345678',
                'user_type': 'CLIENT',
                'password': 'TestPassword123!'
            },
            {
                'email': 'user@bhassurance.com',
                'name': 'Test User',
                'phone_number': '+21687654321',
                'user_type': 'USER',
                'password': 'TestPassword123!'
            }
        ]
        
        for user_data in test_users:
            email = user_data['email']
            if not CustomUser.objects.filter(email=email).exists():
                user = CustomUser.objects.create_user(
                    email=email,
                    name=user_data['name'],
                    phone_number=user_data['phone_number'],
                    user_type=user_data['user_type'],
                    password=user_data['password']
                )
                print(f"✅ Created test user: {email}")
            else:
                print(f"⚠️ Test user already exists: {email}")
        
        print("✅ Test data creation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False

def show_api_endpoints():
    """Show available API endpoints"""
    print("\n📡 Available API Endpoints:")
    print("=" * 40)
    
    endpoints = [
        ("POST", "/api/auth/register/", "Register new user"),
        ("POST", "/api/auth/login/", "Login user"),
        ("POST", "/api/auth/logout/", "Logout user"),
        ("GET", "/api/auth/profile/", "Get user profile"),
        ("PUT", "/api/auth/profile/update/", "Update user profile"),
        ("POST", "/api/auth/change-password/", "Change password"),
        ("POST", "/api/auth/request-password-reset/", "Request password reset"),
        ("POST", "/api/auth/confirm-password-reset/", "Confirm password reset"),
        ("GET", "/api/auth/sessions/", "Get user sessions"),
        ("DELETE", "/api/auth/sessions/{key}/terminate/", "Terminate session"),
        ("DELETE", "/api/auth/sessions/terminate-all/", "Terminate all sessions"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"{method:6} {endpoint:35} - {description}")

def main():
    """Main setup function"""
    try:
        # Setup authentication system
        if setup_authentication():
            # Create test data
            create_test_data()
            
            # Show API endpoints
            show_api_endpoints()
            
            print("\n🎉 BH Assurance Authentication System is ready!")
            print("=" * 60)
        else:
            print("\n❌ Setup failed! Please check the errors above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
