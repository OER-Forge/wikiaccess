# WikiAccess - Quick Start Guide

**Transform DokuWiki into Accessible Documents**

## 🚀 Installation

```bash
# Clone or download the repository
git clone https://github.com/OER-Forge/wikiaccess.git
cd wikiaccess

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

## ⚡ 5-Minute Start

### Method 1: Command Line (Easiest)

```bash
# Convert a DokuWiki page 
wikiaccess https://your-wiki.com page:name -o output

# Convert multiple pages with both HTML and DOCX
wikiaccess https://your-wiki.com page1 page2 -f html docx
```

### Method 2: Simple Python API

```python
from wikiaccess import convert_wiki_page

result = convert_wiki_page(
    wiki_url='https://your-wiki.com',
    page_name='page:name',
    output_dir='output'
)

print(f"✅ Converted! HTML: {result['html']['file_path']}")
print(f"✅ Converted! DOCX: {result['docx']['file_path']}")
```

### Method 3: Run the Example

```bash
python test_dual_conversion.py
```

This will:
1. Convert a DokuWiki page to HTML and Word
2. Check WCAG AA/AAA compliance
3. Generate accessibility reports
4. Open `output/accessibility_report.html` to see results

### Customize for Your Wiki

```python
from scraper import DokuWikiHTTPClient
from html_converter import HTMLConverter
from convert import EnhancedDokuWikiConverter
from a11y_checker import AccessibilityChecker
from reporter import ReportGenerator

# Setup
client = DokuWikiHTTPClient('https://your-wiki.com')
html_conv = HTMLConverter(client)
docx_conv = EnhancedDokuWikiConverter(client)
checker = AccessibilityChecker()
reporter = ReportGenerator('output')

# Convert
url = 'https://your-wiki.com/doku.php?id=your:page'
html_path, html_stats = html_conv.convert_url(url)
docx_stats = docx_conv.convert_url(url, 'output.docx')

# Check & Report
html_report = checker.check_html(html_path)
docx_report = checker.check_docx('output.docx')
reporter.add_page_reports('page_name', html_report, docx_report,
                         html_stats, docx_stats)
reporter.generate_dashboard()
```

## Supported DokuWiki Syntax

| Syntax | Example | Result |
|--------|---------|--------|
| **Heading 1** | `===== Title =====` | # Title (H1) |
| **Heading 2** | `==== Title ====` | ## Title (H2) |
| **Heading 3** | `=== Title ===` | ### Title (H3) |
| **Heading 4** | `== Title ==` | #### Title (H4) |
| **Bold** | `**text**` | **text** |
| **Italic** | `//text//` | *text* |
| **Underline** | `__text__` | <u>text</u> |
| **Link** | `[[url\|text]]` | Hyperlink |
| **Bullet List** | `  * item` | • item |
| **Image** | `{{ path?500 }}` | Image placeholder |
| **YouTube** | `{{ youtube>ID }}` | Link to video |
| **Block Equation** | `$$E=mc^2$$` | Centered equation |
| **Inline Equation** | `$E=mc^2$` | Inline equation |
| **Line Break** | `\\` | New line |

## Accessibility Features

✅ **Always Included:**
- Document title
- Language metadata
- Proper heading hierarchy
- Descriptive link text
- Image alt text
- Semantic structure

## Command Line Usage

```bash
# Run the example
python example.py

# Open the generated document
open output/momentum_principle.docx  # macOS
```

## Testing Accessibility

### Quick Test
1. Open document in Word
2. **File → Info → Check Accessibility**
3. Address any issues found

### Screen Reader Test
- **macOS:** Press `Cmd+F5` for VoiceOver
- **Windows:** Download NVDA (free)

## Common Patterns

### Physics/Math Document
```python
convert_dokuwiki_to_word(
    'physics_notes.txt',
    'physics_notes.docx',
    document_title='Physics 101: Momentum',
    language='en-US'
)
```

### Multi-language Document
```python
convert_dokuwiki_to_word(
    'spanish_doc.txt',
    'spanish_doc.docx',
    document_title='Documento en Español',
    language='es-ES'
)
```

### Batch Processing
```python
from pathlib import Path
from doku2word import convert_dokuwiki_to_word

input_dir = Path('dokuwiki_files')
output_dir = Path('word_docs')
output_dir.mkdir(exist_ok=True)

for txt_file in input_dir.glob('*.txt'):
    output_file = output_dir / f"{txt_file.stem}.docx"
    convert_dokuwiki_to_word(
        str(txt_file),
        str(output_file),
        document_title=txt_file.stem.replace('_', ' ').title()
    )
```

## Troubleshooting

### Import errors
```bash
pip install -r requirements.txt
```

### Document doesn't look right
- Check your DokuWiki syntax
- Ensure proper heading hierarchy
- Verify link format: `[[url|text]]`

### Accessibility warnings
- Run Word's Accessibility Checker
- Read ACCESSIBILITY.md for detailed guide
- Test with screen reader

## File Structure

```
doku2word/
├── doku2word.py          # Main converter module
├── example.py            # Example usage script
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
├── README.md            # Full documentation
├── ACCESSIBILITY.md     # Testing guide
├── LICENSE              # MIT License
├── samples/             # Example input files
│   └── momentum_principle.txt
└── output/              # Generated Word docs
    └── momentum_principle.docx
```

## Next Steps

1. **Try the example:**
   ```bash
   python example.py
   ```

2. **Read full docs:**
   - `README.md` - Complete usage guide
   - `ACCESSIBILITY.md` - Testing guide

3. **Test your documents:**
   - Use Word's Accessibility Checker
   - Test with screen reader
   - Verify heading structure

4. **Customize:**
   - Modify `doku2word.py` for your needs
   - Add more DokuWiki syntax support
   - Enhance accessibility features

## Support

- Read the documentation in `README.md`
- Check `ACCESSIBILITY.md` for testing
- Review code comments in `doku2word.py`

---

**Remember:** Accessible documents benefit everyone! 🌟
