import pandas as pd
import json
import os
from datetime import datetime

def convert_excel_to_json():
    """
    Convert Excel file to JSON format and prepare data for model training
    """
    
    # File paths
    excel_path = "Données_Assurance.xlsx"
    json_path = "assurance_data.json"
    jsonl_path = "assurance_training_data.jsonl"
    
    print("🔄 Loading Excel file...")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        print(f"✅ Successfully loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        print(f"📊 Columns: {df.columns.tolist()}")
        
        # Clean the data
        print("🧹 Cleaning data...")
        
        # Replace NaN values with empty strings or appropriate defaults
        df = df.fillna("")
        
        # Convert to JSON format
        print("🔄 Converting to JSON...")
        
        # Convert DataFrame to list of dictionaries
        data_records = df.to_dict('records')
        
        # Save as JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data_records, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON file saved to {json_path}")
        
        # Prepare training data in JSONL format
        print("🔄 Preparing training data...")
        prepare_training_data(data_records, jsonl_path)
        
        # Display sample data
        print("\n📋 Sample data:")
        for i, record in enumerate(data_records[:3]):
            print(f"Record {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
            print()
            
        return data_records
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def prepare_training_data(data_records, jsonl_path):
    """
    Prepare data for model training in JSONL format
    """
    
    training_examples = []
    
    for record in data_records:
        # Create various training examples based on the insurance data
        
        # Example 1: Company information query
        if record.get('RAISON_SOCIALE') and record.get('LIB_SECTEUR_ACTIVITE'):
            prompt = f"Quelle est l'activité de la société {record['RAISON_SOCIALE']}?"
            completion = f"La société {record['RAISON_SOCIALE']} opère dans le secteur {record['LIB_SECTEUR_ACTIVITE']}."
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
        
        # Example 2: Location-based query
        if record.get('RAISON_SOCIALE') and record.get('VILLE'):
            prompt = f"Où se trouve la société {record['RAISON_SOCIALE']}?"
            completion = f"La société {record['RAISON_SOCIALE']} se trouve à {record['VILLE']}."
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
        
        # Example 3: Fiscal information query
        if record.get('RAISON_SOCIALE') and record.get('MATRICULE_FISCALE'):
            prompt = f"Quel est le matricule fiscal de {record['RAISON_SOCIALE']}?"
            completion = f"Le matricule fiscal de {record['RAISON_SOCIALE']} est {record['MATRICULE_FISCALE']}."
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
        
        # Example 4: Governorate information
        if record.get('RAISON_SOCIALE') and record.get('LIB_GOUVERNORAT'):
            prompt = f"Dans quel gouvernorat se trouve {record['RAISON_SOCIALE']}?"
            completion = f"{record['RAISON_SOCIALE']} se trouve dans le gouvernorat de {record['LIB_GOUVERNORAT']}."
            
            training_examples.append({
                "prompt": prompt + "\n\n###\n\n",
                "completion": " " + completion + " END"
            })
    
    # Save training data as JSONL
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Training data saved to {jsonl_path} with {len(training_examples)} examples")
    
    return training_examples

def analyze_data_quality(data_records):
    """
    Analyze the quality and completeness of the data
    """
    print("\n📊 Data Quality Analysis:")
    print("=" * 50)
    
    if not data_records:
        print("❌ No data to analyze")
        return
    
    total_records = len(data_records)
    print(f"Total records: {total_records}")
    
    # Analyze each column
    for column in data_records[0].keys():
        non_empty_count = sum(1 for record in data_records if record.get(column) and str(record[column]).strip())
        completeness = (non_empty_count / total_records) * 100
        print(f"{column}: {non_empty_count}/{total_records} ({completeness:.1f}% complete)")

if __name__ == "__main__":
    print("🚀 Starting Excel to JSON conversion...")
    print("=" * 50)
    
    data = convert_excel_to_json()
    
    if data:
        analyze_data_quality(data)
        print("\n✅ Conversion completed successfully!")
        print("\nFiles created:")
        print("📄 bhagent/data/assurance_data.json - Full JSON data")
        print("🎯 bhagent/data/assurance_training_data.jsonl - Training data")
    else:
        print("❌ Conversion failed!")
