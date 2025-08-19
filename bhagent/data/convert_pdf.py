import fitz  

# Path to your PDF
pdf_path = "data/raw/CG ASSUR SENIOR.pdf"

# Extract text
doc = fitz.open(pdf_path)
text = ""
for page in doc:
    text += page.get_text()

# Save extracted text to a file
output_path = "data/cg_assur_senior.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Extracted text saved to {output_path}")
