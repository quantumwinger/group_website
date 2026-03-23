from bs4 import BeautifulSoup
import re

with open("publications.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for pub_item in soup.find_all(class_='pub-item'):
    num_div = pub_item.find(class_='pub-number')
    if not num_div: continue
    num = num_div.get_text(strip=True)
    
    # Prepend to the h3
    h3 = pub_item.find('h3')
    if h3:
        # Check if already prepended
        if not h3.get_text().startswith(num + "."):
            # insert "18. " at the start of the h3
            h3.insert(0, num + ". ")
            
    # Remove the num_div
    num_div.decompose()
    
    # Remove light-mode-photo class from pub-photo
    img = pub_item.find(class_='pub-photo')
    if img and 'light-mode-photo' in img.get('class', []):
        img['class'].remove('light-mode-photo')

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Reformatted publication HTML successfully!")
