import urllib.request
import re
from html.parser import HTMLParser

# 1. Fetch text from old site
url = "https://www.drgatksu.com/publications"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        data = data.strip()
        if data:
            self.text.append(data)
parser = TextParser()
parser.feed(html)

# Extract full publications text
pubs_text = []
current_pub = []
num_pattern = re.compile(r'^\d+\)')
for line in parser.text:
    if num_pattern.match(line):
        if current_pub:
            pubs_text.append(current_pub)
        current_pub = [line]
    elif current_pub and not line.startswith("Home") and not line.startswith("Research"):
        current_pub.append(line)
if current_pub:
    pubs_text.append(current_pub)

# Reverse so that index 0 is publication 18, index 1 is 17... Wait, drgatksu.com lists them 18 down to 1.
# Actually, the numbering on drgatksu is "18) Title", "17) Title". So pubs_text is already ordered 18 down to 1.

# 2. Read local publications.html
with open('/Users/quantum_winger/Desktop/website/publications.html', 'r', encoding='utf-8') as f:
    local_html = f.read()

# 3. Inject tooltips
# We will find `<p class="pub-abstract">...</p>` and add the tooltip right after it.
new_html = local_html
for pub in pubs_text:
    # pub is a list of strings: ["18) Title", "Authors, Journal, link", "Abstract part 1", "Abstract part 2..."]
    if len(pub) < 3: continue
    
    number_match = re.search(r'^(\d+)\)', pub[0])
    if not number_match: continue
    num = number_match.group(1)
    
    # The abstract is usually everything after the first 2 or 3 lines.
    # Let's find the first line that doesn't look like authors or link
    abstract_lines = []
    for line in pub[1:]:
        if "http" in line or "doi.org" in line or "[link]" in line:
            continue
        # Also skip author lines if it contains authors
        if "Dasgupta" in line and ("Chem." in line or "Phys." in line or "Lett." in line):
            continue
        abstract_lines.append(line)
        
    full_abstract = " ".join(abstract_lines).strip()
    if not full_abstract: continue
    
    # To reliably inject, we can find the pub-item for this number
    # We look for <div class="pub-number">NUM</div>
    search_str = f'<div class="pub-number">{num}</div>'
    if search_str not in new_html:
        continue
        
    # Find the end of this pub-item div. The safest way is to regex replace the </p> after pub-abstract within this block.
    # Wait, the structure is:
    # <p class="pub-abstract">...</p>
    # <a href="..." class="pub-link">Read Article ↗</a>
    # </div>
    # </div> (end of pub-item)
    
    pub_block_pattern = re.compile(rf'(<div class="pub-number">{num}</div>.*?)(</div>\s*</div>)', re.DOTALL)
    
    match = pub_block_pattern.search(new_html)
    if match:
        block_content = match.group(1)
        # Append the tooltip div at the end of the block content, before the closing divs
        tooltip_html = f'\n                            <div class="pub-abstract-tooltip">{full_abstract}</div>\n                        '
        new_block = block_content + tooltip_html
        new_html = new_html[:match.start()] + new_block + match.group(2) + new_html[match.end():]

with open('/Users/quantum_winger/Desktop/website/publications.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
    
print("Successfully injected abstracts!")
