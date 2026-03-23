from pypdf import PdfReader

with open("pubs.pdf", "rb") as f:
    reader = PdfReader(f)
    with open("pubs.txt", "w", encoding="utf-8") as out:
        for page in reader.pages:
            out.write(page.extract_text() + "\n")
print("extracted")
