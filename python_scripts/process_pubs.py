from bs4 import BeautifulSoup
import re

# 1. Parse the provided HTML file for the full abstracts
with open("Dasgupta Research Group @ K-State - Publications.html", "r", encoding="utf-8") as f:
    source_soup = BeautifulSoup(f.read(), "html.parser")

# In Google Sites, text is usually in <p> or <span>. We'll extract all text blocks that look like publications.
text_blocks = [p.get_text(separator=' ', strip=True) for p in source_soup.find_all(['p', 'div', 'span']) if p.get_text(strip=True)]
# Wait, this might be messy. Let's just use the previous strategy because we know the text is there,
# or we can extract the text from the whole body.
body_text = source_soup.body.get_text(separator='\n', strip=True)

# Split by numbering
import re
pubs_raw = re.split(r'\n(\d+\))\s', body_text)
abstracts = {}
if len(pubs_raw) > 1:
    for i in range(1, len(pubs_raw), 2):
        num = pubs_raw[i]
        content = pubs_raw[i+1]
        lines = content.split('\n')
        # find the abstract (skip title, authors, links)
        abs_lines = []
        for line in lines:
            line = line.strip()
            if not line: continue
            if "http" in line or "[link]" in line or "doi.org" in line: continue
            if "Dasgupta" in line and ("Chem." in line or "Phys." in line or "Lett." in line or "Commun." in line): continue
            
            # The title is usually the first line
            if line == lines[0].strip(): continue
            
            abs_lines.append(line)
        
        abstracts[num] = " ".join(abs_lines).strip()

# 2. Update publications.html
with open("publications.html", "r", encoding="utf-8") as f:
    pub_soup = BeautifulSoup(f.read(), "html.parser")

# Journal mapping
journal_logos = {
    'J. Phys. Chem. Lett.': 'jpcl.png',
    'Chem. Mater.': 'cm.png',
    'Chem. Sci.': None, # Don't have cs.png
    'Phys. Chem. Chem. Phys.': None,
    'Photochem. Photobiol. Sci.': None,
    'J. Chem. Phys.': 'jcp.png',
    'Nature Commun.': 'nc.png',
    'Nat. Commun.': 'nc.png',
    'J. Phys. Chem. A': 'jpca.png',
    'J. Chem. Theory Comput.': 'jctc.png',
    'J. Phys. Chem. B': 'jpcb.png',
    'J. Comp. Chem.': 'jcc.png',
    'J. Am. Chem. Soc.': 'jacs.png',
    'J. Chem. Inf. Model.': 'jcim.png'
}

def get_journal_logo(authors_text):
    for j, logo in journal_logos.items():
        if logo and j in authors_text:
            return logo
    return None

for pub_item in pub_soup.find_all(class_='pub-item'):
    num_div = pub_item.find(class_='pub-number')
    if not num_div: continue
    num = num_div.get_text(strip=True)
    
    # 2a. Update the image block
    # Remove old placeholder
    ph = pub_item.find(class_='photo-placeholder')
    if ph:
        ph.extract()
        
    # See if there's already a pub-image-col, if not create one
    img_col = pub_item.find(class_='pub-image-col')
    if not img_col:
        img_col = pub_soup.new_tag('div', attrs={'class': 'pub-image-col'})
        num_div.insert_after(img_col)
        
        # Add the circular image
        img_tag = pub_soup.new_tag('img', src=f'pubs_images/{num}.png', attrs={'class': 'light-mode-photo pub-photo'})
        img_col.append(img_tag)
        
        # Add the journal logo
        authors_p = pub_item.find(class_='pub-authors')
        if authors_p:
            logo = get_journal_logo(authors_p.get_text())
            if logo:
                logo_tag = pub_soup.new_tag('img', src=f'pubs_images/{logo}', attrs={'class': 'journal-logo'})
                img_col.append(logo_tag)
                
    # 2b. Update the abstract text
    if num in abstracts and abstracts[num]:
        # remove old tooltip if exists
        tt = pub_item.find(class_='pub-abstract-tooltip')
        if tt:
            tt.string = abstracts[num]
        else:
            tt = pub_soup.new_tag('div', attrs={'class': 'pub-abstract-tooltip'})
            tt.string = abstracts[num]
            pub_item.append(tt)
            
    # Add click interaction (we will handle the JS separately, but we can add a cursor pointer class)
    pub_item['style'] = "cursor: pointer;"

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(str(pub_soup))

print("Successfully updated publications!")
