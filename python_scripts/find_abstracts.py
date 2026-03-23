from bs4 import BeautifulSoup
import re

with open("Dasgupta Research Group @ K-State - Publications.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# Find the exact text nodes 
texts_18 = []
texts_17 = []

# Assuming the structure is: Title -> Authors -> Abstract text -> link
# Let's just find the link node and then search backwards for the abstract, or search the document for the abstract text.
body_text = soup.body.get_text(separator='\n\n', strip=True)
print("BODY TEXT EXCERPT AROUND 18:")
lines = body_text.split('\n\n')
for i, line in enumerate(lines):
    if "Reactivity of Nanoconfined Water" in line:
        print("\n".join(lines[i-2:i+10]))
        break

print("\nBODY TEXT EXCERPT AROUND 17:")
for i, line in enumerate(lines):
    if "Intermolecular Interactions Override" in line:
        print("\n".join(lines[i-2:i+10]))
        break
