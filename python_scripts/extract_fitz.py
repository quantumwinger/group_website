import fitz  # PyMuPDF

doc = fitz.open("pubs.pdf")
text = ""
for page in doc:
    text += page.get_text()

with open("pubs_fitz.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Successfully extracted PDF with PyMuPDF")
