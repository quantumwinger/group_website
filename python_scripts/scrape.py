import urllib.request
import re
from html.parser import HTMLParser

url = "https://www.drgatksu.com/publications"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    class TextParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
        def handle_data(self, data):
            self.text.append(data.strip())
            
    parser = TextParser()
    parser.feed(html)
    text_data = [t for t in parser.text if t]
    
    pubs = []
    current_pub = []
    num_pattern = re.compile(r'^\d+\)')
    
    for line in text_data:
        if num_pattern.match(line):
            if current_pub:
                pubs.append(" ".join(current_pub))
            current_pub = [line]
        elif current_pub and len(" ".join(current_pub)) < 1500 and not line.startswith("Home") and not line.startswith("Research"):
            current_pub.append(line)
            
    if current_pub:
        pubs.append(" ".join(current_pub))
        
    for p in pubs:
        print("PUB_START")
        print(p)
        print("PUB_END")
except Exception as e:
    print("Error:", e)
