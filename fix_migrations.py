#!/usr/bin/env python3
"""
Fix Migration Dependencies Script

This script fixes the migration dependency issue by directly updating
the django_migrations table in the database.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhagent.settings')

def fix_migrations():
    """Fix migration dependencies"""
    print("🔧 Fixing Migration Dependencies")
    print("=" * 50)
    
    try:
        # Setup Django without loading models that cause issues
        from django.conf import settings
        from django.db import connection
        
        # Temporarily disable model loading
        settings.INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.sites',
            'rest_framework',
            'rest_framework.authtoken',
            'corsheaders',
        ]
        
        django.setup()
        
        print("✅ Django setup completed")
        
        # Check current migration state
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app, name FROM django_migrations 
                WHERE app IN ('authentication', 'authtoken', 'sites')
                ORDER BY app, name
            """)
            current_migrations = cursor.fetchall()
            
            print(f"📊 Current migration state:")
            for app, name in current_migrations:
                print(f"   ✅ {app}.{name}")
        
        # Insert missing migrations
        missing_migrations = [
            ('authentication', '0001_initial'),
            ('authtoken', '0001_initial'),
            ('authtoken', '0002_auto_20160226_1747'),
            ('authtoken', '0003_tokenproxy'),
            ('authtoken', '0004_alter_tokenproxy_options'),
            ('sites', '0001_initial'),
            ('sites', '0002_alter_domain_unique'),
        ]
        
        print(f"\n🔄 Adding missing migrations...")
        
        with connection.cursor() as cursor:
            for app, name in missing_migrations:
                # Check if migration already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations 
                    WHERE app = %s AND name = %s
                """, [app, name])
                
                if cursor.fetchone()[0] == 0:
                    # Insert the migration record
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied) 
                        VALUES (%s, %s, NOW())
                    """, [app, name])
                    print(f"   ✅ Added {app}.{name}")
                else:
                    print(f"   ⚠️ {app}.{name} already exists")
        
        print(f"\n✅ Migration dependencies fixed!")
        
        # Verify the fix
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app, name FROM django_migrations 
                ORDER BY app, name
            """)
            all_migrations = cursor.fetchall()
            
            print(f"\n📊 Final migration state:")
            for app, name in all_migrations:
                print(f"   ✅ {app}.{name}")
        
        print(f"\n🎉 Migration fix completed successfully!")
        print("You can now run: python manage.py migrate")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing migrations: {e}")
        return False

def create_authentication_tables():
    """Create authentication tables manually if needed"""
    print("\n🔧 Creating Authentication Tables")
    print("=" * 50)
    
    try:
        from django.db import connection
        
        # SQL to create authentication tables
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(17),
                user_type VARCHAR(10) DEFAULT 'CLIENT',
                is_active BOOLEAN DEFAULT TRUE,
                is_staff BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_login TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                profile_picture TEXT,
                bio TEXT,
                password VARCHAR(128) NOT NULL,
                is_superuser BOOLEAN DEFAULT FALSE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES auth_users(id) ON DELETE CASCADE,
                session_key VARCHAR(40) UNIQUE NOT NULL,
                ip_address INET NOT NULL,
                user_agent TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES auth_users(id) ON DELETE CASCADE,
                token UUID UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES auth_users(id) ON DELETE CASCADE,
                token UUID UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE
            );
            """
        ]
        
        with connection.cursor() as cursor:
            for sql in sql_commands:
                try:
                    cursor.execute(sql)
                    print("✅ Table created successfully")
                except Exception as e:
                    if "already exists" in str(e):
                        print("⚠️ Table already exists")
                    else:
                        print(f"❌ Error creating table: {e}")
        
        print("✅ Authentication tables setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def main():
    """Main function"""
    print("🚀 BH Assurance Migration Fix")
    print("=" * 50)
    
    # Fix migrations
    if fix_migrations():
        print("\n🎯 Next Steps:")
        print("1. Run: python manage.py migrate")
        print("2. Create superuser: python manage.py createsuperuser")
        print("3. Start server: python manage.py runserver")
        return 0
    else:
        print("\n❌ Migration fix failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
