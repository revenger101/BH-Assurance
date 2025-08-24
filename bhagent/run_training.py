#!/usr/bin/env python3
"""
Simple script to run training from the correct directory
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Insurance Data Training...")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if training data exists
    training_file = "data/assurance_training_data.jsonl"
    if not os.path.exists(training_file):
        print(f"❌ Training data not found: {training_file}")
        print("Let me create it for you...")
        
        # Run conversion script
        try:
            result = subprocess.run([sys.executable, "data/convert_excel_to_json.py"], 
                                  cwd=os.getcwd(), check=True)
            print("✅ Training data created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create training data: {e}")
            return 1
    else:
        print(f"✅ Training data found: {training_file}")
    
    # Run training script
    try:
        print("\n🎯 Starting model training...")
        result = subprocess.run([sys.executable, "scripts/train_on_insurance_data.py"], 
                              cwd=os.getcwd())
        return result.returncode
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
