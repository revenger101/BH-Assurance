#!/usr/bin/env python3
"""
Client Data Lookup Service
This service provides client information lookup without requiring model training
"""

import sqlite3
import re
try:
    from typing import Optional, Dict
except ImportError:
    # For older Python versions
    Optional = None
    Dict = None

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
            r"What is the profession of (.+?)\?",
            r"What is the birthdate of (.+?)\?",
            r"What is the monthly income of (.+?)\?",
            r"What is the marital status of (.+?)\?",
            r"Who is (.+?)\?",
            r"Tell me about (.+?)\?",
            r"Information about (.+?)\?",
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
        print(f"\nQ: {query}")
        result = service.search_client(query)
        print(f"A: {result}")
    
    print(f"\n📊 Total clients in database: {len(service.list_all_clients())}")
