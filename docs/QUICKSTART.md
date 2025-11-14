# WikiAccess Quick Start Guide

## Installation

### Prerequisites
- **Python 3.8+** with pip
- **Pandoc 2.9+** (for document conversion)  
- **Node.js and npm** (for accessibility testing with pa11y)

```bash
# Clone the repository
git clone https://github.com/OER-Forge/wikiaccess.git
cd wikiaccess

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Pandoc (required for HTML/DOCX conversion)
# macOS:
brew install pandoc

# Linux:
sudo apt-get install pandoc

# Windows: Download from https://pandoc.org/installing.html

# Install Node.js (required for accessibility testing)
# macOS:
brew install node

# Linux:
sudo apt install nodejs npm

# Windows: Download from https://nodejs.org/

# Install pa11y for accessibility testing
npm install pa11y

# Verify installation
python3 -c "from wikiaccess import convert_wiki_page; print('✓ WikiAccess ready')"
pandoc --version
npx pa11y --version
```

## Basic Usage

### Conversion Workflows Overview

WikiAccess supports three primary workflows:

![Conversion Workflows](WORKFLOWS.png)

### 1. Convert a Single Page

```bash
python3 << 'EOF'
from wikiaccess import convert_wiki_page

result = convert_wiki_page(
    wiki_url="https://your-wiki.com",
    page_name="page:name",
    output_dir="output"
)

print(f"HTML: {result['html']['file_path']}")
print(f"DOCX: {result['docx']['file_path']}")
print(f"Accessibility Report: {result['accessibility_report']}")
EOF
```

### 2. Batch Convert from URL List

Create `URLS.txt`:
```
https://your-wiki.com/doku.php?id=page:one
https://your-wiki.com/doku.php?id=page:two
https://your-wiki.com/doku.php?id=page:three
```

Then run:
```bash
python convert_from_file_list.py
```

### 3. Edit Markdown and Re-convert

Edit the markdown files:
```bash
# Edit output/markdown/page_one.md
nano output/markdown/page_one.md
```

Re-convert without scraping:
```bash
# Convert one file
python convert_from_markdown.py output/markdown/page_one.md

# Convert all markdown files
python convert_from_markdown.py
```

## Output Structure

```
output/
├── markdown/
│   ├── page_one.md       ← Edit this
│   ├── page_two.md
│   └── ...
├── images/
│   ├── image1.png
│   ├── image2.jpg
│   └── youtube_[id].jpg  ← YouTube thumbnails
├── html/
│   ├── page_one.html     ← Open in browser
│   └── page_two.html
├── docx/
│   ├── page_one.docx     ← Download
│   └── page_two.docx
└── reports/
    ├── accessibility_report.html    ← Main dashboard
    ├── page_one_accessibility.html
    └── page_two_accessibility.html
```

## Checking Accessibility

Open `output/reports/accessibility_report.html` in a browser to:
- View AA/AAA compliance scores
- See which issues were found
- Access converted HTML and DOCX files
- Check image and equation statistics

## Common Tasks

### Fix Missing Image Alt Text

Edit the markdown and add alt text:

**Before**:
```markdown
![](../images/diagram.png)
```

**After**:
```markdown
![A diagram showing the water cycle](../images/diagram.png)
```

Then re-convert:
```bash
python convert_from_markdown.py output/markdown/page_name.md
```

### Edit Equations

The markdown uses standard LaTeX:

**Inline**:
```markdown
Einstein's equation is $E = mc^2$
```

**Display**:
```markdown
$$
\int_0^\infty e^{-x} dx = 1
$$
```

MathJax renders these automatically in HTML.

### Customize HTML Styling

Edit the CSS in `markdown_converter.py`'s `_enhance_html_accessibility()` method:

```python
css = """
<style>
body {
    font-family: Georgia, serif;
    font-size: 20px;
    /* ... more CSS ... */
}
</style>
"""
```

Then re-convert:
```bash
python convert_from_markdown.py
```

## Troubleshooting

### "Pandoc not found"
```bash
# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc

# Windows
# Download from https://pandoc.org/installing.html
```

### "Images not showing in HTML"
1. Check `output/images/` contains the files
2. Verify markdown has: `![alt](../images/filename.png)`
3. Clear browser cache (Ctrl+Shift+Delete)

### "Equations look wrong in HTML"
- Ensure MathJax script is in HTML `<head>`
- Use `$...$` for inline, `$$...$$` for display
- Clear cache and refresh

### "Word document is empty"
- Pandoc may need more memory: `pandoc --version`
- Try converting smaller markdown files first
- Check markdown syntax is valid

## Advanced Usage

### Custom Output Directory

```python
from wikiaccess import convert_multiple_pages

results = convert_multiple_pages(
    wiki_url="https://wiki.com",
    page_names=["page:one", "page:two"],
    output_dir="my_custom_output"
)
```

### Disable Accessibility Checks

```python
from wikiaccess import convert_wiki_page

result = convert_wiki_page(
    wiki_url="https://wiki.com",
    page_name="page:name",
    check_accessibility=False  # Skip checks
)
```

### Access Conversion Statistics

```python
from wikiaccess import convert_wiki_page

result = convert_wiki_page(
    wiki_url="https://wiki.com",
    page_name="page:name"
)

html_stats = result['html']['stats']
print(f"Images processed: {html_stats['images_success']}/{html_stats['images']}")
```

## Next Steps

1. **Read Full Documentation**: See `docs/MODULE_DOCUMENTATION.md`
2. **Understand Architecture**: View `docs/ARCHITECTURE.d2` and render with D2
3. **See Workflows**: Check `docs/WORKFLOWS.d2` for detailed process flows
4. **Check Source**: Review module code in `wikiaccess/`

## Getting Help

- **Module Documentation**: `docs/MODULE_DOCUMENTATION.md`
- **Architecture Diagrams**: `docs/*.d2` (render with https://d2lang.com)
- **Source Code**: `wikiaccess/*.py` (well-commented)
- **GitHub Issues**: https://github.com/OER-Forge/wikiaccess/issues

## Tips for Best Results

1. **Keep Markdown Clean**: Use proper heading hierarchy (H1 → H2 → H3)
2. **Add Image Alt Text**: Include descriptive text for all images
3. **Use Standard Formatting**: Bold, italic, links use standard Markdown
4. **Test HTML First**: HTML rendering is usually better than DOCX
5. **Check Reports**: Review accessibility reports to find issues
6. **Edit and Retry**: Fix issues in markdown, re-convert without scraping

