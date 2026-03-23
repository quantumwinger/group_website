import re

with open("style.css", "r", encoding="utf-8") as f:
    css = f.read()

# Remove the pub-abstract-tooltip rules
# This regex removes blocks like `.pub-abstract-tooltip { ... }` 
css = re.sub(r'\.pub-abstract-tooltip\s*{[^}]*}', '', css, flags=re.MULTILINE|re.DOTALL)
css = re.sub(r'\.pub-abstract-tooltip::before\s*{[^}]*}', '', css, flags=re.MULTILINE|re.DOTALL)
css = re.sub(r'\.pub-abstract-tooltip::after\s*{[^}]*}', '', css, flags=re.MULTILINE|re.DOTALL)
css = re.sub(r'\.pub-item\.active\s+\.pub-abstract-tooltip\s*{[^}]*}', '', css, flags=re.MULTILINE|re.DOTALL)

# Add our new accordion CSS at the end
accordion_css = """
.pub-abstract {
    display: none;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color);
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.6;
    text-align: justify;
    width: 100%;
    animation: fadeIn 0.3s ease-in forwards;
}

.pub-item.active .pub-abstract {
    display: block;
}
"""

css += accordion_css

with open("style.css", "w", encoding="utf-8") as f:
    f.write(css)

print("CSS updated successfully!")
