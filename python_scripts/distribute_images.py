from bs4 import BeautifulSoup
import os

html_file = "Dasgupta Research Group @ K-State - Publications.html"
with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

images = soup.find_all('img')

for img in images:
    src = img.get('src', '')
    if 'unnamed' in src:
        # Check alt tag or aria-label on img
        desc = img.get('alt', '') or img.get('aria-label', '')
        
        # Check parents for aria-label or title
        if not desc:
            p = img.parent
            for _ in range(5):
                if p:
                    desc = p.get('aria-label', '') or p.get('title', '')
                    if desc: break
                    p = p.parent
        
        # If still no description, maybe it's near some text
        if not desc:
            p = img.parent
            for _ in range(5):
                if p:
                    text = p.get_text(separator=' ', strip=True)
                    if len(text) > 10:
                        desc = text[:100]
                        break
                    p = p.parent
                    
        print(f"{os.path.basename(src)}: {desc}")
