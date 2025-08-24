#!/usr/bin/env python3
"""
Process new Excel files for insurance training data

This script processes:
1. Mapping produits vs profils_cibles.xlsx - Product to target profile mapping
2. Description_garanties.xlsx - Guarantee descriptions

Creates comprehensive Q&A training data for insurance products and guarantees.
"""

import pandas as pd
import json
import os
from pathlib import Path
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InsuranceDataProcessor:
    def __init__(self, data_dir: str = "bhagent/data"):
        self.data_dir = Path(data_dir)
        self.mapping_file = self.data_dir / "Mapping produits vs profils_cibles.xlsx"
        self.guarantees_file = self.data_dir / "Description_garanties.xlsx"
        
    def load_data(self):
        """Load both Excel files"""
        logger.info("Loading Excel files...")
        
        # Load mapping file
        if self.mapping_file.exists():
            self.mapping_df = pd.read_excel(self.mapping_file)
            logger.info(f"✅ Loaded mapping file: {len(self.mapping_df)} rows")
            print(f"Mapping columns: {self.mapping_df.columns.tolist()}")
        else:
            logger.error(f"❌ Mapping file not found: {self.mapping_file}")
            return False
            
        # Load guarantees file
        if self.guarantees_file.exists():
            self.guarantees_df = pd.read_excel(self.guarantees_file)
            logger.info(f"✅ Loaded guarantees file: {len(self.guarantees_df)} rows")
            print(f"Guarantees columns: {self.guarantees_df.columns.tolist()}")
        else:
            logger.error(f"❌ Guarantees file not found: {self.guarantees_file}")
            return False
            
        return True
    
    def generate_mapping_training_data(self) -> List[Dict]:
        """Generate training data from product mapping"""
        logger.info("Generating training data from product mapping...")
        
        training_examples = []
        
        for _, row in self.mapping_df.iterrows():
            branche = row['LIB_BRANCHE']
            sous_branche = row['LIB_SOUS_BRANCHE'] if pd.notna(row['LIB_SOUS_BRANCHE']) else ""
            produit = row['LIB_PRODUIT']
            profils = row['Profils cibles'] if pd.notna(row['Profils cibles']) else ""
            
            # Question 1: What are the target profiles for a product?
            if profils:
                prompt = f"Quels sont les profils cibles pour le produit {produit}?"
                completion = f"Les profils cibles pour le produit {produit} sont: {profils}."
                
                training_examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
            
            # Question 2: What branch does a product belong to?
            prompt = f"À quelle branche appartient le produit {produit}?"
            completion = f"Le produit {produit} appartient à la branche {branche}."
            if sous_branche:
                completion += f" Plus spécifiquement, il fait partie de la sous-branche {sous_branche}."
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
            
            # Question 3: What products are available in a branch?
            if branche not in [ex['branch'] for ex in training_examples if 'branch' in ex]:
                branch_products = self.mapping_df[self.mapping_df['LIB_BRANCHE'] == branche]['LIB_PRODUIT'].tolist()
                if len(branch_products) > 1:
                    prompt = f"Quels sont les produits disponibles dans la branche {branche}?"
                    products_list = ", ".join(branch_products[:5])  # Limit to first 5
                    completion = f"Dans la branche {branche}, les produits disponibles incluent: {products_list}."
                    
                    training_examples.append({
                        "prompt": prompt + "\n\n###\n\n",
                        "completion": " " + completion + " END",
                        "branch": branche  # Helper field to avoid duplicates
                    })
            
            # Question 4: Who should buy this product?
            if profils:
                prompt = f"Qui devrait acheter le produit {produit}?"
                completion = f"Le produit {produit} est recommandé pour: {profils}."
                
                training_examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
        
        # Remove helper fields
        for example in training_examples:
            if 'branch' in example:
                del example['branch']
        
        logger.info(f"Generated {len(training_examples)} examples from mapping data")
        return training_examples
    
    def generate_guarantees_training_data(self) -> List[Dict]:
        """Generate training data from guarantees descriptions"""
        logger.info("Generating training data from guarantees descriptions...")
        
        training_examples = []
        
        for _, row in self.guarantees_df.iterrows():
            branche = row['LIB_BRANCHE']
            sous_branche = row['LIB_SOUS_BRANCHE'] if pd.notna(row['LIB_SOUS_BRANCHE']) else ""
            produit = row['LIB_PRODUIT']
            garantie = row['LIB_GARANTIE']
            description = row['Description'] if pd.notna(row['Description']) else ""
            
            if not description:
                continue
                
            # Question 1: What does this guarantee cover?
            prompt = f"Que couvre la garantie {garantie}?"
            completion = f"La garantie {garantie} couvre: {description}"
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
            
            # Question 2: What guarantees are available for a product?
            prompt = f"Quelles sont les garanties disponibles pour le produit {produit}?"
            # Get all guarantees for this product
            product_guarantees = self.guarantees_df[
                self.guarantees_df['LIB_PRODUIT'] == produit
            ]['LIB_GARANTIE'].tolist()
            
            if len(product_guarantees) > 1:
                guarantees_list = ", ".join(list(set(product_guarantees))[:5])  # Unique, limit to 5
                completion = f"Pour le produit {produit}, les garanties disponibles incluent: {guarantees_list}."
                
                training_examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
            
            # Question 3: Detailed guarantee description
            if len(description) > 50:  # Only for substantial descriptions
                prompt = f"Pouvez-vous expliquer en détail la garantie {garantie} du produit {produit}?"
                completion = f"La garantie {garantie} du produit {produit}: {description}"
                
                training_examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
            
            # Question 4: What product offers this guarantee?
            prompt = f"Quel produit offre la garantie {garantie}?"
            completion = f"La garantie {garantie} est offerte par le produit {produit}"
            if branche:
                completion += f" dans la branche {branche}"
            completion += "."
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
        
        # Remove duplicates based on prompt
        seen_prompts = set()
        unique_examples = []
        for example in training_examples:
            if example['prompt'] not in seen_prompts:
                unique_examples.append(example)
                seen_prompts.add(example['prompt'])
        
        logger.info(f"Generated {len(unique_examples)} unique examples from guarantees data")
        return unique_examples
    
    def save_training_data(self, training_examples: List[Dict]):
        """Save training data to files"""
        logger.info("Saving training data...")
        
        # Save as JSONL for training
        output_file = self.data_dir / "new_excel_training_data.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ Training data saved to {output_file}")
        
        # Save as JSON for inspection
        json_file = self.data_dir / "new_excel_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(training_examples, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ JSON data saved to {json_file}")
        
        # Save summary
        summary = {
            "total_examples": len(training_examples),
            "mapping_file_rows": len(self.mapping_df),
            "guarantees_file_rows": len(self.guarantees_df),
            "files_processed": [
                "Mapping produits vs profils_cibles.xlsx",
                "Description_garanties.xlsx"
            ]
        }
        
        summary_file = self.data_dir / "new_excel_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Summary saved to {summary_file}")
        
        return len(training_examples)

def main():
    print("🚀 Processing New Excel Files for Insurance Training")
    print("=" * 60)
    
    processor = InsuranceDataProcessor()
    
    # Load data
    if not processor.load_data():
        print("❌ Failed to load data files")
        return 1
    
    # Generate training data from mapping
    mapping_examples = processor.generate_mapping_training_data()
    
    # Generate training data from guarantees
    guarantees_examples = processor.generate_guarantees_training_data()
    
    # Combine all examples
    all_examples = mapping_examples + guarantees_examples
    
    print(f"\n📊 Training Data Summary:")
    print(f"   📋 Mapping examples: {len(mapping_examples)}")
    print(f"   🛡️ Guarantees examples: {len(guarantees_examples)}")
    print(f"   📈 Total examples: {len(all_examples)}")
    
    # Save training data
    total_saved = processor.save_training_data(all_examples)
    
    print(f"\n✅ Processing completed!")
    print(f"📊 Generated {total_saved} training examples")
    print("\nFiles created:")
    print("📄 bhagent/data/new_excel_training_data.jsonl - Training data")
    print("📋 bhagent/data/new_excel_data.json - JSON format")
    print("📈 bhagent/data/new_excel_summary.json - Summary")
    
    # Show sample examples
    print(f"\n🔍 Sample training examples:")
    for i, example in enumerate(all_examples[:3]):
        print(f"\nExample {i+1}:")
        print(f"  Q: {example['prompt'].replace('###', '').strip()}")
        print(f"  A: {example['completion'].replace(' END', '').strip()}")

if __name__ == "__main__":
    main()
