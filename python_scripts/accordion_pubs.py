import re
from bs4 import BeautifulSoup

# Read the HTML
with open("publications.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# Read the PDF text
with open("pubs.txt", "r", encoding="utf-8") as f:
    pdf_text = f.read()

# We need to extract the abstract text for 1 to 18 from pdf_text.
# Structure in pubs.txt:
# "18) Reactivity of..."
# "S. Dasgupta*,  S. Saha and F. Paesani*.  J. Phys. Chem. Lett. 16, 11996 (2025)) link\n"
# "The reactivity of water..."
# Let's cleanly split using regex. Each publication starts with "NUM)".
pubs_raw = re.split(r'\n(\d+)\)\s*', '\n' + pdf_text)
# pubs_raw[0] is garbage.
# pubs_raw[1] is '18', pubs_raw[2] is the text for 18, etc.

abstracts = {}
for i in range(1, len(pubs_raw), 2):
    num = pubs_raw[i]
    content = pubs_raw[i+1].strip()
    
    # Content has the title, the authors, and then the abstract.
    # We want everything AFTER the "link" word, or just extract the last big chunk.
    # The abstract is usually a big block of text.
    lines = content.split('\n')
    abs_lines = []
    found_link = False
    for line in lines:
        line = line.strip()
        # skip garbage lines that came from the PDF headers/footers
        if "Dasgupta Research Group" in line: continue
        if "Home Research About" in line: continue
        if "3/23/26, " in line: continue
        if "https://" in line and "publications" in line: continue
        
        if "link" in line.lower()[-6:] and not found_link:
            found_link = True
            continue
        
        if found_link and line:
            abs_lines.append(line)
            
    # Some publications might not have "link". If found_link is false, fallback:
    if not found_link:
        # Just grab lines that don't look like authors or title.
        pass
        
    abstract_text = " ".join(abs_lines).strip()
    abstracts[num] = abstract_text

# Update HTML
for pub in soup.find_all(class_='pub-item'):
    # Remove existing tooltips and pub-abstracts
    for el in pub.find_all(class_='pub-abstract-tooltip'):
        el.decompose()
    for el in pub.find_all(class_='pub-abstract'):
        el.decompose()
        
    # Get the publication number from the h3
    h3 = pub.find('h3')
    if not h3: continue
    title_text = h3.get_text()
    match = re.search(r'^(\d+)\.', title_text)
    if not match: continue
    num = match.group(1)
    
    if num in abstracts and abstracts[num]:
        # Create a new accordion abstract div
        # Place it inside pub-details at the end
        details = pub.find(class_='pub-details')
        if details:
            abs_div = soup.new_tag('div', attrs={'class': 'pub-abstract'})
            abs_div.string = abstracts[num]
            details.append(abs_div)

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Accordion abstracts injected!")
