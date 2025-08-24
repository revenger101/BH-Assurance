#!/usr/bin/env python3
"""
PDF Data Extraction and Training Data Preparation

This script extracts text from PDF files (including OCR for scanned images)
and prepares training data for the insurance model.

Features:
- Extract text from regular PDFs
- OCR for scanned images within PDFs
- Clean and structure the extracted text
- Generate Q&A pairs for training
- Support for French insurance documents
"""

import os
import json
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from pathlib import Path
import logging
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, pdf_dir: str = "bhagent/data/raw", output_dir: str = "bhagent/data"):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure Tesseract for French OCR
        self.tesseract_config = r'--oem 3 --psm 6 -l fra+eng'
        
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using both text extraction and OCR"""
        logger.info(f"Processing: {pdf_path.name}")
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # First, try to extract text directly
                text = page.get_text()
                
                # If no text or very little text, use OCR
                if len(text.strip()) < 50:
                    logger.info(f"  Page {page_num + 1}: Using OCR (little/no text found)")
                    text = self.ocr_page(page)
                else:
                    logger.info(f"  Page {page_num + 1}: Text extracted directly")
                
                full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            
            doc.close()
            return self.clean_text(full_text)
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {str(e)}")
            return ""
    
    def ocr_page(self, page) -> str:
        """Perform OCR on a PDF page"""
        try:
            # Convert page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")

            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_data))

            # Perform OCR
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            return text

        except Exception as e:
            logger.warning(f"OCR failed (Tesseract may not be installed): {str(e)}")
            logger.info("Continuing without OCR - only extractable text will be used")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Fix common OCR errors for French text
        replacements = {
            'é': 'é', 'è': 'è', 'ê': 'ê', 'ë': 'ë',
            'à': 'à', 'â': 'â', 'ä': 'ä',
            'ù': 'ù', 'û': 'û', 'ü': 'ü',
            'ô': 'ô', 'ö': 'ö',
            'î': 'î', 'ï': 'ï',
            'ç': 'ç',
            'É': 'É', 'È': 'È', 'Ê': 'Ê',
            'À': 'À', 'Â': 'Â',
            'Ù': 'Ù', 'Û': 'Û',
            'Ô': 'Ô',
            'Î': 'Î',
            'Ç': 'Ç'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    def extract_all_pdfs(self) -> Dict[str, str]:
        """Extract text from all PDFs in the directory"""
        logger.info(f"Starting PDF extraction from {self.pdf_dir}")
        
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        extracted_data = {}
        
        for pdf_file in pdf_files:
            text = self.extract_text_from_pdf(pdf_file)
            if text:
                extracted_data[pdf_file.stem] = text
                logger.info(f"✅ Extracted {len(text)} characters from {pdf_file.name}")
            else:
                logger.warning(f"❌ No text extracted from {pdf_file.name}")
        
        return extracted_data
    
    def generate_training_data(self, extracted_data: Dict[str, str]) -> List[Dict]:
        """Generate training Q&A pairs from extracted PDF data"""
        logger.info("Generating training data from PDF content...")
        
        training_examples = []
        
        for filename, content in extracted_data.items():
            # Generate different types of questions based on content
            examples = self.create_qa_pairs(filename, content)
            training_examples.extend(examples)
        
        logger.info(f"Generated {len(training_examples)} training examples")
        return training_examples
    
    def create_qa_pairs(self, filename: str, content: str) -> List[Dict]:
        """Create Q&A pairs from PDF content"""
        examples = []
        
        # Clean filename for better questions
        clean_name = filename.replace("CG ", "").replace("_", " ").replace("-", " ")
        
        # Split content into sections
        sections = content.split('\n\n')
        meaningful_sections = [s.strip() for s in sections if len(s.strip()) > 100]
        
        # Generate different types of questions
        for i, section in enumerate(meaningful_sections[:5]):  # Limit to first 5 sections
            
            # Question about document content
            if "assurance" in clean_name.lower():
                prompt = f"Que contient le document {clean_name}?"
                completion = f"Le document {clean_name} contient des informations sur {section[:200]}..."
                
                examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
            
            # Question about specific terms
            if "conditions générales" in content.lower() or "CG" in filename:
                prompt = f"Quelles sont les conditions générales pour {clean_name}?"
                completion = f"Les conditions générales pour {clean_name} incluent: {section[:300]}..."
                
                examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
            
            # Question about coverage
            if any(word in content.lower() for word in ["couverture", "garantie", "protection"]):
                prompt = f"Quelle est la couverture offerte par {clean_name}?"
                completion = f"La couverture de {clean_name} comprend: {section[:250]}..."
                
                examples.append({
                    "prompt": prompt + "\n\n###\n\n",
                    "completion": " " + completion + " END"
                })
        
        return examples
    
    def save_data(self, extracted_data: Dict[str, str], training_data: List[Dict]):
        """Save extracted data and training examples"""
        
        # Save raw extracted text
        raw_output = self.output_dir / "pdf_extracted_text.json"
        with open(raw_output, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Raw text saved to {raw_output}")
        
        # Save training data
        training_output = self.output_dir / "pdf_training_data.jsonl"
        with open(training_output, 'w', encoding='utf-8') as f:
            for example in training_data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        logger.info(f"✅ Training data saved to {training_output}")
        
        # Save summary
        summary = {
            "total_pdfs": len(extracted_data),
            "total_training_examples": len(training_data),
            "pdf_files": list(extracted_data.keys()),
            "extraction_date": str(Path().cwd())
        }
        
        summary_output = self.output_dir / "pdf_extraction_summary.json"
        with open(summary_output, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Summary saved to {summary_output}")

def main():
    print("🚀 PDF Data Extraction and Training Preparation")
    print("=" * 60)
    
    # Check if required packages are installed
    try:
        import fitz
        import pytesseract
        from PIL import Image
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install: pip install PyMuPDF pytesseract Pillow")
        return
    
    # Initialize extractor
    extractor = PDFExtractor()
    
    # Extract text from all PDFs
    print("\n📄 Extracting text from PDF files...")
    extracted_data = extractor.extract_all_pdfs()
    
    if not extracted_data:
        print("❌ No data extracted from PDFs")
        return
    
    # Generate training data
    print("\n🎯 Generating training data...")
    training_data = extractor.generate_training_data(extracted_data)
    
    # Save results
    print("\n💾 Saving results...")
    extractor.save_data(extracted_data, training_data)
    
    print("\n✅ PDF extraction completed!")
    print(f"📊 Processed {len(extracted_data)} PDF files")
    print(f"🎯 Generated {len(training_data)} training examples")
    print("\nFiles created:")
    print("📄 bhagent/data/pdf_extracted_text.json - Raw extracted text")
    print("🎯 bhagent/data/pdf_training_data.jsonl - Training data")
    print("📋 bhagent/data/pdf_extraction_summary.json - Summary")

if __name__ == "__main__":
    main()
