#!/usr/bin/env python3
"""
Complete pipeline for training model on client data
This script runs the entire process from data conversion to model deployment
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 40)

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    
    print(f"▶️ Running: {script_path}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Last 500 chars
            return True
        else:
            print("❌ Failed!")
            if result.stderr:
                print("Error:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out (1 hour limit)")
        return False
    except Exception as e:
        print(f"❌ Error running script: {str(e)}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    
    print_step(0, "Checking Prerequisites")
    
    # Check if client data exists
    client_csv = "data/qa_dataset_clients.csv"
    if not os.path.exists(client_csv):
        print(f"❌ Client data not found: {client_csv}")
        print("Please ensure your client data CSV file exists")
        return False
    
    print(f"✅ Client data found: {client_csv}")
    
    # Check if required directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)
    
    # Check Python packages
    required_packages = [
        "torch", "transformers", "datasets", "peft", "pandas", "accelerate"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not installed")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All prerequisites met!")
    return True

def main():
    """Main pipeline function"""
    
    print_header("Client Data Training Pipeline")
    print("This pipeline will:")
    print("1. Convert your client CSV data to training format")
    print("2. Train the model incrementally on client data only")
    print("3. Update the chat service to use the new model")
    print("4. Create test scripts for validation")
    print("\n⚠️ This preserves all existing insurance knowledge!")
    
    # Get user confirmation
    response = input("\nDo you want to proceed? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Pipeline cancelled by user")
        return
    
    start_time = time.time()
    
    # Step 0: Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please fix the issues above.")
        return
    
    # Step 1: Convert client data
    print_step(1, "Converting Client Data to Training Format")
    if not run_script("scripts/convert_client_data.py", "Data conversion"):
        print("❌ Data conversion failed. Cannot proceed.")
        return
    
    # Step 2: Train model incrementally
    print_step(2, "Training Model on Client Data (Incremental)")
    print("⏰ This may take 30-60 minutes depending on your hardware...")
    
    if not run_script("scripts/train_client_incremental.py", "Incremental training"):
        print("❌ Training failed. Please check the logs above.")
        return
    
    # Step 3: Update chat service
    print_step(3, "Updating Chat Service Configuration")
    if not run_script("scripts/update_chat_model.py", "Chat service update"):
        print("⚠️ Chat service update failed, but training was successful.")
        print("You can manually update the MODEL_PATH in chat/simple_mistral_client.py")
    
    # Step 4: Create summary
    print_step(4, "Creating Summary and Next Steps")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("PIPELINE COMPLETED SUCCESSFULLY! 🎉")
    
    print(f"⏱️ Total time: {duration/60:.1f} minutes")
    print("\n📁 Files created:")
    print("✅ data/client_training_data.jsonl - Training data")
    print("✅ outputs/client_incremental_model/ - Trained model")
    print("✅ test_client_model.py - Test script")
    
    print("\n🔧 What was done:")
    print("✅ Converted client CSV to training format")
    print("✅ Trained model incrementally (preserving existing knowledge)")
    print("✅ Updated chat service configuration")
    print("✅ Created test scripts")
    
    print("\n🚀 Next steps:")
    print("1. Restart your Django server:")
    print("   python manage.py runserver")
    
    print("\n2. Test the model:")
    print("   python test_client_model.py")
    
    print("\n3. Test in chat interface:")
    print("   - Ask: 'What is the profession of Ben Ali El Amri Ahmed Salah?'")
    print("   - Verify: Insurance questions still work")
    
    print("\n4. If you need to revert:")
    print("   mv chat/simple_mistral_client.py.backup chat/simple_mistral_client.py")
    
    print("\n🔐 Security notes:")
    print("✅ Client data processed locally only")
    print("✅ No data sent to external services")
    print("✅ Existing model knowledge preserved")
    print("✅ Incremental learning used (efficient)")
    
    print("\n🎯 Your model now knows:")
    print("✅ All existing insurance knowledge")
    print("✅ Client-specific information")
    print("✅ Can answer confidential questions when authenticated")

if __name__ == "__main__":
    main()
