#!/usr/bin/env python3
"""
Install requirements for PDF processing and OCR
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR is already installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Tesseract OCR not found")
    return False

def install_tesseract_windows():
    """Instructions for installing Tesseract on Windows"""
    print("\n🔧 To install Tesseract OCR on Windows:")
    print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Install the .exe file")
    print("3. Add Tesseract to your PATH, or set TESSDATA_PREFIX")
    print("4. Restart your command prompt")
    print("\nAlternatively, if you have chocolatey:")
    print("   choco install tesseract")

def main():
    print("🚀 Installing PDF Processing Requirements")
    print("=" * 50)
    
    # Required Python packages
    packages = [
        "PyMuPDF",      # For PDF processing
        "pytesseract",  # OCR wrapper
        "Pillow",       # Image processing
    ]
    
    print("📦 Installing Python packages...")
    
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
    
    print("\n🔍 Checking Tesseract OCR...")
    
    if not check_tesseract():
        system = platform.system()
        if system == "Windows":
            install_tesseract_windows()
        elif system == "Linux":
            print("\n🔧 To install Tesseract on Linux:")
            print("Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-fra")
            print("CentOS/RHEL: sudo yum install tesseract tesseract-langpack-fra")
        elif system == "Darwin":  # macOS
            print("\n🔧 To install Tesseract on macOS:")
            print("brew install tesseract tesseract-lang")
    
    print("\n✅ Installation completed!")
    print("\n📋 Next steps:")
    print("1. If Tesseract was just installed, restart your terminal")
    print("2. Run: python bhagent/data/extract_pdf_data.py")

if __name__ == "__main__":
    main()
