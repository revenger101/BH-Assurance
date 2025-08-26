#!/usr/bin/env python3
"""
Simple Migration Fix Script

This script directly connects to PostgreSQL and fixes the migration issues
without loading Django models.
"""

import psycopg2
from datetime import datetime

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="BH Assurance",
            user="postgres",
            password="jaja619jaja",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def fix_migration_dependencies():
    """Fix migration dependencies by updating django_migrations table"""
    print("🔧 Fixing Migration Dependencies")
    print("=" * 50)
    
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check current migrations
        cursor.execute("""
            SELECT app, name FROM django_migrations 
            ORDER BY app, name
        """)
        current_migrations = cursor.fetchall()
        
        print("📊 Current migrations:")
        for app, name in current_migrations:
            print(f"   ✅ {app}.{name}")
        
        # Add missing migrations
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
        
        for app, name in missing_migrations:
            # Check if migration exists
            cursor.execute("""
                SELECT COUNT(*) FROM django_migrations 
                WHERE app = %s AND name = %s
            """, (app, name))
            
            if cursor.fetchone()[0] == 0:
                # Insert migration record
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES (%s, %s, %s)
                """, (app, name, datetime.now()))
                print(f"   ✅ Added {app}.{name}")
            else:
                print(f"   ⚠️ {app}.{name} already exists")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Migration dependencies fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing migrations: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def create_authentication_tables():
    """Create authentication tables"""
    print("\n🔧 Creating Authentication Tables")
    print("=" * 50)
    
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create authentication tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            )
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
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES auth_users(id) ON DELETE CASCADE,
                token UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES auth_users(id) ON DELETE CASCADE,
                token UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS authtoken_token (
                key VARCHAR(40) PRIMARY KEY,
                user_id UUID UNIQUE REFERENCES auth_users(id) ON DELETE CASCADE,
                created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS django_site (
                id SERIAL PRIMARY KEY,
                domain VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL
            )
            """,
        ]
        
        for table_sql in tables:
            try:
                cursor.execute(table_sql)
                print("✅ Table created/verified")
            except Exception as e:
                print(f"⚠️ Table issue: {e}")
        
        # Insert default site if not exists
        cursor.execute("""
            INSERT INTO django_site (id, domain, name) 
            VALUES (1, 'localhost:8000', 'BH Assurance')
            ON CONFLICT (id) DO NOTHING
        """)
        
        conn.commit()
        print("✅ Authentication tables setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function"""
    print("🚀 BH Assurance Simple Migration Fix")
    print("=" * 50)
    
    # Test database connection
    conn = connect_to_database()
    if not conn:
        print("❌ Cannot connect to database. Please check:")
        print("   - PostgreSQL is running")
        print("   - Database 'BH Assurance' exists")
        print("   - Username: postgres, Password: 123456")
        return 1
    
    conn.close()
    print("✅ Database connection successful")
    
    # Fix migrations
    if fix_migration_dependencies():
        print("✅ Migration dependencies fixed")
    else:
        print("❌ Failed to fix migration dependencies")
        return 1
    
    # Create tables
    if create_authentication_tables():
        print("✅ Authentication tables created")
    else:
        print("❌ Failed to create authentication tables")
        return 1
    
    print(f"\n🎉 Migration fix completed successfully!")
    print("\n🎯 Next Steps:")
    print("1. Try: python manage.py migrate")
    print("2. If that works, create superuser: python manage.py createsuperuser")
    print("3. Start server: python manage.py runserver")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
