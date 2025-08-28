#!/usr/bin/env python3
"""
Create a client data lookup system
This creates a simple database lookup for client information without training
"""

import os
import json
import pandas as pd
import sqlite3
from pathlib import Path

def create_client_database():
    """Create SQLite database from client CSV data"""
    
    print("🔐 Creating Client Data Lookup System")
    print("=" * 50)
    
    # Load client CSV
    client_csv = "bhagent/data/qa_dataset_clients.csv"
    if not os.path.exists(client_csv):
        print(f"❌ Client data not found: {client_csv}")
        return False
    
    print(f"📂 Loading client data from: {client_csv}")
    df = pd.read_csv(client_csv)
    print(f"✅ Loaded {len(df)} client records")
    
    # Create database
    db_path = "bhagent/data/client_database.db"
    conn = sqlite3.connect(db_path)
    
    # Parse the questions and answers to extract structured data
    client_data = {}
    
    for _, row in df.iterrows():
        question = str(row['question']).strip()
        answer = str(row['answer']).strip()
        
        # Extract name from question
        if "What is the profession of" in question:
            name = question.replace("What is the profession of", "").replace("?", "").strip()
            if name not in client_data:
                client_data[name] = {}
            client_data[name]['profession'] = answer
            
        elif "What is the birthdate of" in question:
            name = question.replace("What is the birthdate of", "").replace("?", "").strip()
            if name not in client_data:
                client_data[name] = {}
            client_data[name]['birthdate'] = answer
            
        elif "What is the monthly income of" in question:
            name = question.replace("What is the monthly income of", "").replace("?", "").strip()
            if name not in client_data:
                client_data[name] = {}
            client_data[name]['monthly_income'] = answer
            
        elif "What is the marital status of" in question:
            name = question.replace("What is the marital status of", "").replace("?", "").strip()
            if name not in client_data:
                client_data[name] = {}
            client_data[name]['marital_status'] = answer
    
    # Create table
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            profession TEXT,
            birthdate TEXT,
            monthly_income TEXT,
            marital_status TEXT
        )
    ''')
    
    # Insert data
    for name, data in client_data.items():
        cursor.execute('''
            INSERT OR REPLACE INTO clients 
            (name, profession, birthdate, monthly_income, marital_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            name,
            data.get('profession', ''),
            data.get('birthdate', ''),
            data.get('monthly_income', ''),
            data.get('marital_status', '')
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created database with {len(client_data)} unique clients")
    print(f"📁 Database saved to: {db_path}")
    
    return True

def create_lookup_service():
    """Create a lookup service for client data"""
    
    lookup_service_code = '''#!/usr/bin/env python3
"""
Client Data Lookup Service
This service provides client information lookup without requiring model training
"""

import sqlite3
import re
from typing import Optional, Dict

class ClientLookupService:
    def __init__(self, db_path: str = "bhagent/data/client_database.db"):
        self.db_path = db_path
    
    def search_client(self, query: str) -> Optional[str]:
        """Search for client information based on query"""
        
        # Extract name from query
        name = self._extract_name_from_query(query)
        if not name:
            return None
        
        # Connect to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search for client
            cursor.execute(
                "SELECT * FROM clients WHERE name LIKE ?", 
                (f"%{name}%",)
            )
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            # Parse result
            _, name, profession, birthdate, monthly_income, marital_status = result
            
            # Determine what information to return based on query
            query_lower = query.lower()
            
            if "profession" in query_lower:
                return profession if profession else "Profession not available"
            elif "birthdate" in query_lower or "birth" in query_lower:
                return birthdate if birthdate else "Birthdate not available"
            elif "income" in query_lower or "salary" in query_lower:
                return monthly_income if monthly_income else "Income not available"
            elif "marital" in query_lower or "married" in query_lower:
                return marital_status if marital_status else "Marital status not available"
            else:
                # Return general information
                info = []
                if profession:
                    info.append(f"Profession: {profession}")
                if birthdate:
                    info.append(f"Birthdate: {birthdate}")
                if monthly_income:
                    info.append(f"Monthly Income: {monthly_income}")
                if marital_status:
                    info.append(f"Marital Status: {marital_status}")
                
                return "; ".join(info) if info else "No information available"
                
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def _extract_name_from_query(self, query: str) -> Optional[str]:
        """Extract client name from query"""
        
        # Common patterns
        patterns = [
            r"What is the profession of (.+?)\\?",
            r"What is the birthdate of (.+?)\\?",
            r"What is the monthly income of (.+?)\\?",
            r"What is the marital status of (.+?)\\?",
            r"Who is (.+?)\\?",
            r"Tell me about (.+?)\\?",
            r"Information about (.+?)\\?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, try to find a name-like string
        words = query.split()
        if len(words) >= 3:
            # Look for capitalized words that might be names
            potential_names = []
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 2:
                    potential_names.append(word)
            
            if len(potential_names) >= 2:
                return " ".join(potential_names[:4])  # Take up to 4 words
        
        return None
    
    def list_all_clients(self) -> list:
        """List all clients in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM clients ORDER BY name")
            results = cursor.fetchall()
            conn.close()
            return [row[0] for row in results]
        except Exception as e:
            print(f"Database error: {e}")
            return []

# Test the service
if __name__ == "__main__":
    service = ClientLookupService()
    
    # Test queries
    test_queries = [
        "What is the profession of Ben Ali El Amri Ahmed Salah?",
        "What is the birthdate of Ben Ali El Amri Ahmed Salah?",
        "Who is Ben Ali El Amri Ahmed Salah?",
        "Tell me about Ben Ali El Amri Ahmed Salah",
    ]
    
    print("🧪 Testing Client Lookup Service")
    print("=" * 40)
    
    for query in test_queries:
        print(f"\\nQ: {query}")
        result = service.search_client(query)
        print(f"A: {result}")
    
    print(f"\\n📊 Total clients in database: {len(service.list_all_clients())}")
'''
    
    # Save the lookup service
    service_path = "chat/client_lookup_service.py"
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(lookup_service_code)
    
    print(f"✅ Created lookup service: {service_path}")
    return service_path

def integrate_with_chat():
    """Create integration code for the chat service"""
    
    integration_code = '''
# Add this to your chat/simple_mistral_client.py

from .client_lookup_service import ClientLookupService

# Initialize client lookup service
client_lookup = ClientLookupService()

def enhanced_chat_completion(message, max_tokens=150):
    """Enhanced chat completion with client data lookup"""
    
    # First, try client lookup
    client_info = client_lookup.search_client(message)
    
    if client_info:
        # Found client information
        return client_info
    else:
        # Fall back to regular AI model
        return chat_completion(message, max_tokens)
'''
    
    integration_path = "chat/integration_example.py"
    with open(integration_path, 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    print(f"✅ Created integration example: {integration_path}")

def main():
    """Main function"""
    
    print("🚀 Client Data Lookup System Setup")
    print("=" * 50)
    print("This creates a fast lookup system for client data without model training")
    print()
    
    # Step 1: Create database
    if not create_client_database():
        print("❌ Failed to create database")
        return
    
    # Step 2: Create lookup service
    service_path = create_lookup_service()
    
    # Step 3: Create integration example
    integrate_with_chat()
    
    print("\n🎉 SUCCESS! Client lookup system created!")
    print("\n📁 Files created:")
    print("✅ bhagent/data/client_database.db - SQLite database")
    print("✅ chat/client_lookup_service.py - Lookup service")
    print("✅ chat/integration_example.py - Integration code")
    
    print("\n🧪 Testing the service...")
    
    # Test the service
    try:
        exec(open(service_path).read())
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n🔧 Next steps:")
    print("1. The lookup service can answer client questions instantly")
    print("2. No model training required - uses direct database lookup")
    print("3. Integrate with your chat service using the example code")
    print("4. Test with: 'What is the profession of Ben Ali El Amri Ahmed Salah?'")

if __name__ == "__main__":
    main()
