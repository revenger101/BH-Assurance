#!/usr/bin/env python3
"""
Update chat service to use the client-trained model
This script updates the model path in the chat service configuration
"""

import os
import shutil
from pathlib import Path

def backup_current_config():
    """Backup current chat configuration"""
    
    chat_config_file = "chat/simple_mistral_client.py"
    
    if os.path.exists(chat_config_file):
        backup_file = chat_config_file + ".backup"
        shutil.copy2(chat_config_file, backup_file)
        print(f"✅ Backed up current config to: {backup_file}")
        return True
    else:
        print(f"⚠️ Chat config file not found: {chat_config_file}")
        return False

def update_model_path():
    """Update the model path in chat service"""
    
    chat_config_file = "chat/simple_mistral_client.py"
    client_model_path = "outputs/client_incremental_model"
    
    # Check if client model exists
    if not os.path.exists(client_model_path):
        print(f"❌ Client model not found: {client_model_path}")
        print("Please run training first: python scripts/train_client_incremental.py")
        return False
    
    # Read current config
    try:
        with open(chat_config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace MODEL_PATH
        lines = content.split('\n')
        updated_lines = []
        model_path_updated = False
        
        for line in lines:
            if line.strip().startswith('MODEL_PATH =') or line.strip().startswith('MODEL_PATH='):
                # Update the model path
                updated_lines.append(f'MODEL_PATH = "{client_model_path}"  # Updated to use client-trained model')
                model_path_updated = True
                print(f"✅ Updated MODEL_PATH to: {client_model_path}")
            else:
                updated_lines.append(line)
        
        if not model_path_updated:
            print("⚠️ MODEL_PATH not found in config file")
            print("Please manually update the model path")
            return False
        
        # Write updated config
        with open(chat_config_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ Updated chat configuration: {chat_config_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {str(e)}")
        return False

def test_model_loading():
    """Test if the updated model can be loaded"""
    
    print("🧪 Testing model loading...")
    
    try:
        # Import the updated chat client
        import sys
        sys.path.append('chat')
        
        # Try to import and test
        from simple_mistral_client import chat_completion
        
        # Test with a simple question
        test_response = chat_completion("Hello, how are you?", max_tokens=50)
        
        if test_response and len(test_response.strip()) > 0:
            print("✅ Model loading test successful!")
            print(f"📝 Test response: {test_response[:100]}...")
            return True
        else:
            print("❌ Model loaded but no response generated")
            return False
            
    except Exception as e:
        print(f"❌ Model loading test failed: {str(e)}")
        return False

def create_test_script():
    """Create a test script for client questions"""
    
    test_script_content = '''#!/usr/bin/env python3
"""
Test script for client-trained model
"""

import sys
import os
sys.path.append('chat')

from simple_mistral_client import chat_completion

def test_client_questions():
    """Test the model with client-specific questions"""
    
    print("🧪 Testing client-trained model...")
    print("=" * 50)
    
    # Test questions
    test_questions = [
        "What is the profession of Ben Ali El Amri Ahmed Salah?",
        "Quelle est la profession de Ben Ali El Amri Ahmed Salah?",
        "Who is Ben Ali El Amri Ahmed Salah?",
        "Tell me about insurance policies",  # Test existing knowledge
        "What is BH Assurance?",  # Test existing knowledge
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\\nQuestion {i}: {question}")
        print("-" * 40)
        
        try:
            response = chat_completion(question, max_tokens=150)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\\n✅ Testing completed!")

if __name__ == "__main__":
    test_client_questions()
'''
    
    test_script_path = "test_client_model.py"
    
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write(test_script_content)
    
    print(f"✅ Created test script: {test_script_path}")
    return test_script_path

def main():
    """Main function to update chat service"""
    
    print("🔄 Updating Chat Service to Use Client-Trained Model")
    print("=" * 60)
    
    # Step 1: Backup current configuration
    print("1. Backing up current configuration...")
    backup_success = backup_current_config()
    
    # Step 2: Update model path
    print("\\n2. Updating model path...")
    update_success = update_model_path()
    
    if not update_success:
        print("❌ Failed to update model path")
        return
    
    # Step 3: Test model loading
    print("\\n3. Testing model loading...")
    test_success = test_model_loading()
    
    # Step 4: Create test script
    print("\\n4. Creating test script...")
    test_script = create_test_script()
    
    # Summary
    print("\\n" + "=" * 60)
    if update_success and test_success:
        print("🎉 SUCCESS! Chat service updated successfully!")
        print("\\nWhat was done:")
        print("✅ Backed up original configuration")
        print("✅ Updated MODEL_PATH to use client-trained model")
        print("✅ Verified model can be loaded")
        print("✅ Created test script")
        
        print("\\nNext steps:")
        print("1. Restart your Django server:")
        print("   python manage.py runserver")
        print("2. Test client questions in the chat interface")
        print("3. Run the test script:")
        print(f"   python {test_script}")
        print("4. Verify both client data and insurance knowledge work")
        
    else:
        print("❌ Update failed. Please check the errors above.")
        
        if backup_success:
            print("\\n🔄 To restore original configuration:")
            print("   mv chat/simple_mistral_client.py.backup chat/simple_mistral_client.py")

if __name__ == "__main__":
    main()
