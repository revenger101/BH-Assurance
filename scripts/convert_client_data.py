#!/usr/bin/env python3
"""
Convert client CSV data to training format for incremental learning
This script converts qa_dataset_clients.csv to JSONL format for model training
"""

import os
import pandas as pd
import json
from pathlib import Path

def convert_client_csv_to_jsonl():
    """Convert client CSV to JSONL training format"""
    
    print("🔐 Converting confidential client data for training...")
    print("=" * 60)
    
    # File paths
    client_csv = "bhagent/data/qa_dataset_clients.csv"
    output_jsonl = "bhagent/data/client_training_data.jsonl"
    
    # Check if client data exists
    if not os.path.exists(client_csv):
        print(f"❌ Client data not found: {client_csv}")
        print("Please ensure the qa_dataset_clients.csv file exists in the data folder")
        return None
    
    try:
        # Load client data
        print(f"📂 Loading client data from: {client_csv}")
        df = pd.read_csv(client_csv, encoding='utf-8')
        print(f"✅ Loaded {len(df)} client records")
        print(f"📊 Columns found: {list(df.columns)}")
        
        # Display sample data (first few rows)
        print("\n📋 Sample client data:")
        print(df.head(3).to_string())
        
        # Prepare training examples
        training_examples = []
        
        for index, row in df.iterrows():
            # Check if we have question and answer columns
            if 'question' in df.columns and 'answer' in df.columns:
                question = str(row['question']).strip()
                answer = str(row['answer']).strip()
                
                # Skip empty or NaN values
                if pd.isna(row['question']) or pd.isna(row['answer']) or not question or not answer:
                    continue
                
                # Create training example in the format expected by the model
                training_example = {
                    "prompt": question + "\n\n###\n\n",
                    "completion": " " + answer + " END"
                }
                
                training_examples.append(training_example)
            
            else:
                # If columns are different, try to infer the structure
                print("⚠️ Standard 'question' and 'answer' columns not found")
                print("Available columns:", list(df.columns))
                
                # Try to create training examples from available data
                # This assumes the CSV might have name and profession columns
                if len(df.columns) >= 2:
                    # Use first column as identifier and second as answer
                    identifier = str(row.iloc[0]).strip()
                    value = str(row.iloc[1]).strip()
                    
                    if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]) and identifier and value:
                        # Create question-answer pair
                        question = f"What is the profession of {identifier}?"
                        answer = value
                        
                        training_example = {
                            "prompt": question + "\n\n###\n\n",
                            "completion": " " + answer + " END"
                        }
                        
                        training_examples.append(training_example)
        
        if not training_examples:
            print("❌ No valid training examples could be created from the data")
            print("Please check the CSV format and ensure it has proper question-answer pairs")
            return None
        
        # Save training data as JSONL
        print(f"\n💾 Saving training data to: {output_jsonl}")
        os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
        
        with open(output_jsonl, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✅ Successfully created {len(training_examples)} training examples")
        print(f"📁 Training data saved to: {output_jsonl}")
        
        # Display sample training examples
        print("\n📋 Sample training examples:")
        for i, example in enumerate(training_examples[:3]):
            print(f"\nExample {i+1}:")
            print(f"  Prompt: {example['prompt'][:100]}...")
            print(f"  Completion: {example['completion'][:100]}...")
        
        return output_jsonl
        
    except Exception as e:
        print(f"❌ Error converting client data: {str(e)}")
        return None

def validate_training_data(jsonl_file):
    """Validate the created training data"""
    
    print(f"\n🔍 Validating training data: {jsonl_file}")
    
    try:
        examples = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    example = json.loads(line.strip())
                    examples.append(example)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON error on line {line_num}: {e}")
                    return False
        
        print(f"✅ Validation passed: {len(examples)} valid examples")
        
        # Check format
        required_keys = ['prompt', 'completion']
        for i, example in enumerate(examples[:5]):
            for key in required_keys:
                if key not in example:
                    print(f"❌ Missing key '{key}' in example {i+1}")
                    return False
        
        print("✅ All examples have required format")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False

def main():
    """Main conversion function"""
    
    print("🚀 Starting client data conversion...")
    print("=" * 60)
    
    # Convert CSV to JSONL
    output_file = convert_client_csv_to_jsonl()
    
    if output_file:
        # Validate the output
        if validate_training_data(output_file):
            print("\n🎉 Client data conversion completed successfully!")
            print(f"📁 Training data ready: {output_file}")
            print("\nNext steps:")
            print("1. Run: python scripts/train_client_incremental.py")
            print("2. The model will be trained on client data only")
            print("3. Existing insurance knowledge will be preserved")
        else:
            print("\n❌ Validation failed. Please check the data format.")
    else:
        print("\n❌ Conversion failed. Please check the input data.")

if __name__ == "__main__":
    main()
