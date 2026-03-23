import os, glob

html_files = glob.glob('*.html')

for fpath in html_files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Favicon
    if '<link rel="icon"' not in content:
        content = content.replace('</head>', '    <link rel="icon" href="logo.png" type="image/png">\n</head>')

    # Scholar
    content = content.replace('href="#" class="social-circle" title="Google Scholar"', 'href="https://scholar.google.com/citations?user=fo_lKHMAAAAJ&hl=en&oi=ao" class="social-circle" title="Google Scholar" target="_blank"')
    content = content.replace('href="#" class="social-circle">🎓</a>', 'href="https://scholar.google.com/citations?user=fo_lKHMAAAAJ&hl=en&oi=ao" class="social-circle" target="_blank">🎓</a>')

    # ORCID
    content = content.replace('href="#" class="social-circle" title="ORCID"', 'href="https://orcid.org/0000-0002-8014-8376" class="social-circle" title="ORCID" target="_blank"')
    content = content.replace('href="#" class="social-circle">iD</a>', 'href="https://orcid.org/0000-0002-8014-8376" class="social-circle" target="_blank">iD</a>')

    # LinkedIn
    content = content.replace('href="#" class="social-circle" title="LinkedIn"', 'href="https://www.linkedin.com/feed/" class="social-circle" title="LinkedIn" target="_blank"')
    content = content.replace('href="#" class="social-circle"><span', 'href="https://www.linkedin.com/feed/" class="social-circle" target="_blank"><span')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
