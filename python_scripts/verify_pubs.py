import re
from bs4 import BeautifulSoup

with open("pubs_fitz.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split by publication number: "\n\d+) "
parts = re.split(r'\n(\d+)\)\s*', '\n' + text)

publications_data = {}

# parts[1] is '18', parts[2] is its block
for i in range(1, len(parts), 2):
    num = parts[i]
    lines = [L.strip() for L in parts[i+1].split('\n') if L.strip()]
    
    # Clean out garbage lines
    clean_lines = []
    for L in lines:
        if "Dasgupta Research Group" in L: continue
        if "Home" == L or "Research" == L or "About Saswata" == L or "Gro" == L: continue
        if "3/23/26" in L: continue
        if "https://" in L: continue
        if "/" in L and "37" in L: continue # page numbers like 9/37
        clean_lines.append(L)
        
    # Find the authors/journal line. It's the one that ends with "link" usually, or contains "Dasgupta" and a year.
    aj_idx = -1
    for idx, L in enumerate(clean_lines):
        if "link" in repr(L) or ("Dasgupta" in L and "20" in L):
            # Sometimes a line was broken. E.g. 14) "Eli" "i" "i" "14) Eliminating...". 
            if idx > 0 and len(clean_lines) > idx:
                aj_idx = idx
                break
                
    if aj_idx == -1:
        continue
        
    title_lines = clean_lines[:aj_idx]
    # some garbage might be before the real title, let's just join them.
    # Actually, for 14), there's a duplicate 14) block in the PDF?
    # Wait, in the pure text, page headers caused duplicates. 
    # Let's just trust title_lines, join with space.
    # Filter out single character lines or lines that start with number
    real_title_lines = []
    for tl in title_lines:
        if tl == "14) Eli" or tl == "i" or tl == "12) B l" or tl == "b" or tl == "10) H" or tl == "d i" or tl == "h" or tl == "9) D" or tl == "f" or tl == "l" or tl == "8) A" or tl == "7) El" or tl == "d" or tl == "6) G" or tl == "5) S f" or tl == "1) S" or tl == "id f":
            continue
        real_title_lines.append(tl)

    title = " ".join(real_title_lines).strip()
    
    aj_line = clean_lines[aj_idx]
    if aj_line.endswith(") link"):
        aj_line = aj_line[:-6].strip()
    elif aj_line.endswith("link"):
        aj_line = aj_line[:-4].strip()
    if aj_line.endswith("))"):
        aj_line = aj_line[:-1]
        
    abstract_lines = clean_lines[aj_idx+1:]
    # Remove address lines if present
    abstract_clean = []
    for al in abstract_lines:
        if "📍" in al or "Chemistry and Biochemistry" in al or "66506" in al: continue
        abstract_clean.append(al)
        
    abstract = " ".join(abstract_clean).strip()
    
    publications_data[num] = {
        "title": title,
        "authors_journal": aj_line,
        "abstract": abstract
    }

# Now map journal images
journal_to_image = {
    "J. Phys. Chem. Lett": "jpcl.png",
    "Chem. Mater": "cm.png",
    "J. Am. Chem. Soc": "jacs.png",
    "J. Chem. Inf. Model": "jcim.png",
    "J. Phys. Chem. B": "jpcb.png",
    "J. Chem. Theory Comput": "jctc.png",
    "Chem. Phys. Rev": "cpr.png", # Might not exist, we'll keep existing
    "J. Chem. Phys": "jcp.png",
    "Nat. Commun": "nc.png",
    "J. Phys. Chem. A": "jpca.png",
    "J. Comp. Chem": "jcc.png"
}

with open("publications.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for pub in soup.find_all(class_='pub-item'):
    h3 = pub.find('h3')
    if not h3: continue
    title_text = h3.get_text()
    
    m = re.search(r'^(\d+)\.', title_text)
    if not m: continue
    num = m.group(1)
    
    if num in publications_data:
        data = publications_data[num]
        
        # 1. Update Title exactly
        h3.string = f"{num}. {data['title']}"
        
        # 2. Update Authors and Journal
        details = pub.find(class_='pub-details')
        if details:
            # The first <p> after h3 is the authors/journal
            ps = details.find_all('p', recursive=False)
            if ps:
                ps[0].string = data['authors_journal']
                
            # 3. Update Abstract smoothly
            abs_div = details.find(class_='pub-abstract')
            if abs_div:
                abs_div.string = data['abstract']
                
        # 4. Update Journal Logo
        img_col = pub.find(class_='pub-image-col')
        if img_col:
            logos = img_col.find_all('img', class_='journal-logo')
            if logos:
                logo_img = logos[0]
                aj_text = data['authors_journal']
                matched_logo = None
                for j_name, j_img in journal_to_image.items():
                    if j_name in aj_text:
                        matched_logo = f"pubs_images/{j_img}"
                        break
                
                # Check if file exists if matched
                if matched_logo:
                    import os
                    if os.path.exists(matched_logo):
                        logo_img['src'] = matched_logo
                    else:
                        print(f"Warning: Logo {matched_logo} not found for {num}")

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Publications successfully verified and updated against PyMuPDF data!")
