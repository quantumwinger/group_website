from bs4 import BeautifulSoup
import re

with open("Dasgupta Research Group @ K-State - Publications.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# Get text with space separator, so "1" and "8" might become "1 8" or "18"
text = soup.body.get_text(separator=' ', strip=True)

# Let's clean up spaces before ')' to help parsing
# e.g., "1 8 )" -> "18 )"  -> actually let's just use regex to find the start of each pub
import re

# A publication starts with a number, maybe separated by spaces, then a ')'.
# Regex to match: " 1 8 ) " or " 18 ) "
# We can find all matches and split
pubs_raw = re.split(r'\s(?=\d+\s*\))', text)

abstracts = {}
for chunk in pubs_raw:
    match = re.search(r'^(\d+)\s*\)', chunk)
    if match:
        num = match.group(1)
        # remove the "18 ) title" and authors part
        lines = chunk.split(' ')
        # Actually splitting by space is bad for reading lines.
        # Let's just use the text before next number.
        pass

# Since the user's local html is just an export of their google site, and I have a perfect parser for the live google site:
import urllib.request
url = "https://www.drgatksu.com/publications"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

from html.parser import HTMLParser
class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        d = data.strip()
        if d: self.text.append(d)
p = TextParser()
p.feed(html)

pubs_online = {}
current_pub = []
for line in p.text:
    if re.match(r'^\d+\)', line):
        if current_pub:
            num = re.match(r'^(\d+)\)', current_pub[0]).group(1)
            pubs_online[num] = current_pub
        current_pub = [line]
    elif current_pub and not line.startswith("Home") and not line.startswith("Research"):
        current_pub.append(line)
if current_pub:
    num = re.match(r'^(\d+)\)', current_pub[0]).group(1)
    pubs_online[num] = current_pub

for num, pub_lines in pubs_online.items():
    abs_lines = []
    for line in pub_lines[1:]:
        if "http" in line or "[link]" in line or "doi.org" in line: continue
        if "Dasgupta" in line and ("Chem." in line or "Phys." in line or "Lett." in line or "Commun." in line): continue
        if line == pub_lines[0]: continue
        abs_lines.append(line)
    
    abstracts[num] = " ".join(abs_lines).strip()

# Now patch publications.html directly with 18 and 17
with open("publications.html", "r", encoding="utf-8") as f:
    pub_soup = BeautifulSoup(f.read(), "html.parser")

for pub_item in pub_soup.find_all(class_='pub-item'):
    num_div = pub_item.find(class_='pub-number')
    if not num_div: continue
    num = num_div.get_text(strip=True)
    
    if num in ["18", "17"] and num in abstracts:
        tt = pub_item.find(class_='pub-abstract-tooltip')
        if not tt:
            tt = pub_soup.new_tag('div', attrs={'class': 'pub-abstract-tooltip'})
            pub_item.append(tt)
        tt.string = abstracts[num]

with open("publications.html", "w", encoding="utf-8") as f:
    f.write(str(pub_soup))

print("Patched 18 and 17")
