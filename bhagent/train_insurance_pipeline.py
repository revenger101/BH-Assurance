#!/usr/bin/env python3
"""
Complete Insurance Data Training Pipeline

This script provides a complete pipeline for:
1. Converting Excel data to JSON and training format
2. Training the model on insurance data
3. Testing the trained model

Usage:
    python train_insurance_pipeline.py --step convert    # Convert Excel to JSON
    python train_insurance_pipeline.py --step train     # Train the model
    python train_insurance_pipeline.py --step test      # Test the model
    python train_insurance_pipeline.py --step all       # Run all steps
"""

import argparse
import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step_name):
    """Print a formatted step"""
    print(f"\n📋 Step: {step_name}")
    print("-" * 40)

def check_requirements():
    """Check if required files and dependencies exist"""
    print_step("Checking Requirements")
    
    # Check if Excel file exists
    excel_file = Path("bhagent/data/Données_Assurance.xlsx")
    if not excel_file.exists():
        print(f"❌ Excel file not found: {excel_file}")
        print("Please ensure the Excel file is in the correct location.")
        return False
    else:
        print(f"✅ Excel file found: {excel_file}")
    
    # Check Python packages
    required_packages = [
        "pandas", "torch", "transformers", "datasets", 
        "trl", "peft", "bitsandbytes", "openpyxl"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False
    
    return True

def convert_data():
    """Convert Excel data to JSON and training format"""
    print_header("Converting Excel Data to JSON")
    
    try:
        # Run the conversion script
        result = subprocess.run([
            sys.executable, "bhagent/data/convert_excel_to_json.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Data conversion completed successfully!")
            print(result.stdout)
            
            # Verify output files
            json_file = Path("bhagent/data/assurance_data.json")
            jsonl_file = Path("bhagent/data/assurance_training_data.jsonl")
            
            if json_file.exists() and jsonl_file.exists():
                print(f"✅ Output files created:")
                print(f"   📄 {json_file}")
                print(f"   🎯 {jsonl_file}")
                
                # Show file sizes
                json_size = json_file.stat().st_size / 1024  # KB
                jsonl_size = jsonl_file.stat().st_size / 1024  # KB
                print(f"   📊 JSON file: {json_size:.1f} KB")
                print(f"   📊 JSONL file: {jsonl_size:.1f} KB")
                
                return True
            else:
                print("❌ Output files not created properly")
                return False
        else:
            print("❌ Data conversion failed!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False

def train_model():
    """Train the model on insurance data"""
    print_header("Training Model on Insurance Data")
    
    # Check if training data exists
    training_file = Path("bhagent/data/assurance_training_data.jsonl")
    if not training_file.exists():
        print(f"❌ Training data not found: {training_file}")
        print("Please run the conversion step first.")
        return False
    
    try:
        print("🎯 Starting model training...")
        print("⚠️ This may take a while depending on your hardware...")
        
        # Run the training script
        result = subprocess.run([
            sys.executable, "bhagent/scripts/train_on_insurance_data.py"
        ], cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Model training completed successfully!")
            
            # Check if output directory exists
            output_dir = Path("outputs/sft_mistral_insurance")
            if output_dir.exists():
                print(f"✅ Model saved to: {output_dir}")
                return True
            else:
                print("⚠️ Training completed but output directory not found")
                return False
        else:
            print("❌ Model training failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def test_model():
    """Test the trained model"""
    print_header("Testing Trained Model")
    
    # Check if model exists
    model_dir = Path("outputs/sft_mistral_insurance")
    if not model_dir.exists():
        print(f"❌ Trained model not found: {model_dir}")
        print("Please run the training step first.")
        return False
    
    try:
        print("🧪 Running model tests...")
        
        # Run the test script
        result = subprocess.run([
            sys.executable, "bhagent/scripts/test_insurance_model.py"
        ], cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Model testing completed!")
            return True
        else:
            print("❌ Model testing failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def show_summary():
    """Show a summary of created files and next steps"""
    print_header("Pipeline Summary")
    
    files_to_check = [
        ("Excel Data", "bhagent/data/Données_Assurance.xlsx"),
        ("JSON Data", "bhagent/data/assurance_data.json"),
        ("Training Data", "bhagent/data/assurance_training_data.jsonl"),
        ("Trained Model", "outputs/sft_mistral_insurance"),
    ]
    
    print("📋 File Status:")
    for name, path in files_to_check:
        if Path(path).exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (not found)")
    
    print("\n🎯 Next Steps:")
    print("1. Use the interactive test mode:")
    print("   python bhagent/scripts/test_insurance_model.py --interactive")
    print("\n2. Integrate the model into your application")
    print("\n3. Fine-tune further with additional data if needed")

def main():
    parser = argparse.ArgumentParser(description="Insurance Data Training Pipeline")
    parser.add_argument("--step", choices=["convert", "train", "test", "all"], 
                       default="all", help="Which step to run")
    
    args = parser.parse_args()
    
    print_header("Insurance Data Training Pipeline")
    print("This pipeline will convert your Excel data to JSON and train a model on it.")
    
    # Check requirements first
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return 1
    
    success = True
    
    if args.step in ["convert", "all"]:
        success &= convert_data()
    
    if args.step in ["train", "all"] and success:
        success &= train_model()
    
    if args.step in ["test", "all"] and success:
        success &= test_model()
    
    # Show summary
    show_summary()
    
    if success:
        print("\n🎉 Pipeline completed successfully!")
        return 0
    else:
        print("\n❌ Pipeline completed with errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
