from pdf2image import convert_from_path
import pytesseract

pdf_path = "data/raw/CG ASSUR SENIOR.pdf"
output_text = "data/cg_assur_senior.txt"

# Convert PDF pages to images
pages = convert_from_path(pdf_path)

full_text = ""
for i, page in enumerate(pages):
    text = pytesseract.image_to_string(page, lang='eng')  # 'fra' for French PDFs
    full_text += text + "\n\n"

# Save extracted text
with open(output_text, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Extracted text saved to {output_text}")
