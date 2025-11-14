# WikiAccess

**Transform DokuWiki into Accessible Documents**

Convert DokuWiki pages to WCAG-compliant HTML and Microsoft Word documents with comprehensive accessibility reporting.

## ✨ Features

### Dual-Format Output
- 📄 **Accessible HTML**: MathJax 3 equations, semantic HTML5, high contrast + dark mode
- 📄 **MS Word (DOCX)**: Native OMML equations, embedded media, full accessibility metadata

### Rich Content Support
- 🌐 **Live Wiki Fetching**: Converts pages directly from DokuWiki URLs (no API needed)
- 📐 **Native Equations**: LaTeX → MathJax (HTML) & OMML (Word) - fully editable
- 🖼️ **Image Embedding**: Auto-downloads and embeds with alt-text
- 🎥 **YouTube Videos**: HTML iframes & Word thumbnails with links
- 🔗 **Link Resolution**: Internal wiki links → full URLs

### Accessibility First
- ♿ **WCAG 2.1 AA/AAA**: Comprehensive compliance checking
- 📊 **Accessibility Reports**: Detailed HTML dashboards with success/failure tracking
- 🎯 **Media Statistics**: Track image/video embedding success rates
- � **Issue Detection**: Identifies heading hierarchy, contrast, alt-text issues

### Equation Support

**HTML Output (MathJax 3)**:
- Client-side rendering with accessibility support
- Inline: `\(...\)` and Display: `\[...\]` delimiters
- High contrast and dark mode compatible

**Word Output (OMML)**:
- Native Word equation objects (click to edit)
- Block equations: `$$\vec{r} = \langle x, y, z \rangle$$` → Centered
- Inline equations: `$r_x$` → Inline flow
- Complex LaTeX: fractions, superscripts, subscripts, vectors, Greek letters

### Accessibility Reporting

WikiAccess generates comprehensive accessibility reports showing:
- **WCAG AA/AAA scores** for both HTML and Word outputs
- **Media statistics**: Success/failure rates for images and videos
- **Issue detection**: Heading hierarchy, color contrast, alt-text problems
- **Side-by-side comparison**: HTML vs DOCX compliance scores
- **Clickable links**: Direct access to converted files

## 🚀 Installation

### Option 1: Install as Package (Recommended)

```bash
# Clone repository
git clone https://github.com/OER-Forge/wikiaccess.git
cd wikiaccess

# Install in virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Option 2: From Source

```bash
# Clone repository
git clone https://github.com/OER-Forge/wikiaccess.git
cd wikiaccess

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements
- Python 3.7+
- python-docx ≥0.8.11
- beautifulsoup4 ≥4.12.0
- lxml ≥4.9.0
- Pillow ≥10.0.0
- requests ≥2.31.0
- latex2mathml ≥3.0.0

## 📖 Quick Start

### Simple High-Level API

```python
from wikiaccess import convert_wiki_page

# Convert a single page with all features
result = convert_wiki_page(
    wiki_url='https://wiki.example.com',
    page_name='page:name',
    output_dir='output',
    formats=['html', 'docx'],
    check_accessibility=True
)

print(f"HTML: {result['html']['file_path']}")
print(f"DOCX: {result['docx']['file_path']}")
print(f"Report: {result['accessibility_report']}")
```

### Command Line Interface

```bash
# Convert single page
wikiaccess https://wiki.example.com page:name -o output

# Convert multiple pages
wikiaccess https://wiki.example.com page1 page2 page3 -f html docx

# HTML only, no accessibility checks
wikiaccess https://wiki.example.com page:name -f html --no-accessibility
```

### Advanced Modular Usage

```python
from wikiaccess import (
    DokuWikiHTTPClient, 
    HTMLConverter, 
    EnhancedDokuWikiConverter,
    AccessibilityChecker,
    ReportGenerator
)

# Initialize components
client = DokuWikiHTTPClient('https://wiki.example.com')
html_converter = HTMLConverter(client)
docx_converter = EnhancedDokuWikiConverter(client)
checker = AccessibilityChecker()

# Convert page
url = 'https://wiki.example.com/doku.php?id=page:name'

# HTML output
html_path, html_stats = html_converter.convert_url(url)

# Word output  
docx_stats = docx_converter.convert_url(url, 'output.docx')

# Check accessibility
html_report = checker.check_html(html_path)
docx_report = checker.check_docx('output.docx')

# Generate reports
reporter.add_page_reports('page_name', html_report, docx_report, 
                         html_stats, docx_stats)
reporter.generate_detailed_reports()
reporter.generate_dashboard()
```

### Simple Test Conversion

```bash
# Run the included test script
python test_dual_conversion.py

# Opens accessibility dashboard at: output/accessibility_report.html
# HTML files: output/html/*.html
# DOCX files: output/docx/*.docx
```

## 📂 Project Structure

```
wikiaccess/
├── scraper.py              # HTTP client for fetching wiki pages
├── doku2word.py            # Core DokuWiki parser
├── html_converter.py       # HTML output with MathJax
├── convert.py              # Word (DOCX) output with OMML
├── word_equation.py        # LaTeX → OMML converter
├── a11y_checker.py         # WCAG compliance validator
├── reporter.py             # Accessibility report generator
├── test_dual_conversion.py # Example conversion script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── QUICKSTART.md           # Quick usage guide
├── USAGE.md                # Detailed documentation
├── ACCESSIBILITY.md        # Accessibility compliance details
└── OMML_IMPLEMENTATION.md  # Technical: equation conversion
```

## 📚 Documentation

### Quick Start
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Get started in 5 minutes with installation and examples

### Comprehensive Documentation (docs/ folder)
- **[docs/README.md](docs/README.md)** - Complete documentation overview and navigation  
- **[docs/MODULE_DOCUMENTATION.md](docs/MODULE_DOCUMENTATION.md)** - Full API reference and module details
- **[docs/ACCESSIBILITY_SCORING.md](docs/ACCESSIBILITY_SCORING.md)** - How WCAG 2.1 scores are calculated
- **[docs/ARCHITECTURE.png](docs/ARCHITECTURE.png)** - System architecture diagram
- **[docs/WORKFLOWS.png](docs/WORKFLOWS.png)** - Conversion workflow diagrams  
- **[docs/DATA_FLOW.png](docs/DATA_FLOW.png)** - Data transformation flow

### Legacy Documentation
- **[USAGE.md](USAGE.md)** - Detailed usage examples (legacy)
- **[ACCESSIBILITY.md](ACCESSIBILITY.md)** - WCAG compliance guide (legacy)
- **[OMML_IMPLEMENTATION.md](OMML_IMPLEMENTATION.md)** - How equation conversion works

## Supported DokuWiki Syntax

| Syntax | Example | HTML Output | Word Output |
|--------|---------|-------------|-------------|
| Headings | `=== Heading ===` | `<h3>` | Heading 3 style |
| Bold | `**text**` | `<strong>` | Bold |
| Italic | `//text//` | `<em>` | Italic |
| Underline | `__text__` | `<u>` | Underline |
| Links | `[[url\|text]]` | `<a href>` | Hyperlink |
| Lists | `  * item` | `<ul><li>` | Bullet list |
| Block equations | `$$E=mc^2$$` | MathJax display | OMML centered |
| Inline equations | `$x^2$` | MathJax inline | OMML inline |
| Images | `{{path?width\|alt}}` | `<img>` embedded | Picture embedded |
| YouTube | `{{youtube>ID}}` | `<iframe>` | Thumbnail + link |

## 🧪 Output Examples

After conversion, you get:

1. **HTML File** (`output/html/*.html`)
   - Clean semantic HTML5
   - MathJax 3 for equations
   - Embedded images and videos
   - High contrast + dark mode CSS

2. **Word File** (`output/docx/*.docx`)
   - Native Word equation objects (editable)
   - Embedded images with alt-text
   - Video thumbnails with links
   - Full accessibility metadata

3. **Accessibility Reports** (`output/*.html`)
   - Dashboard with all pages
   - Detailed per-page reports
   - WCAG AA/AAA scores
   - Media conversion statistics
   - Issue lists with recommendations

## 🎯 Use Cases

- **Educational Content**: Convert course materials to accessible formats
- **Documentation**: Transform technical wikis into distributable documents
- **Compliance**: Generate WCAG-compliant HTML and Word documents
- **Archival**: Export wiki content with full media embedding
- **Publishing**: Create print-ready documents from collaborative wikis

## ⚠️ Known Limitations

- **LaTeX**: Complex features (matrices, integrals, limits) may need manual adjustment
- **Tables**: Not yet supported (coming soon)
- **Plugins**: Some advanced DokuWiki plugins may not convert
- **Authentication**: Basic auth supported, complex SSO may need customization

## 🏆 Accessibility Standards

WikiAccess targets:
- **WCAG 2.1 Level AA** (primary target)
- **WCAG 2.1 Level AAA** (stretch goal)
- **Section 508** compliance
- Semantic structure for screen readers
- Keyboard navigation support

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Table support
- More LaTeX features
- Additional DokuWiki syntax
- Performance optimizations
- Custom styling templates

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [python-docx](https://python-docx.readthedocs.io/) - Word document generation
- [MathJax](https://www.mathjax.org/) - Math rendering for HTML
- [latex2mathml](https://github.com/roniemartinez/latex2mathml) - LaTeX parsing
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

---

**WikiAccess** - *Transform DokuWiki into Accessible Documents*

Made with ❤️ for accessible education and documentation

[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG-2.1%20AA-green.svg)](https://www.w3.org/WAI/WCAG21/quickref/?currentsidebar=%23col_customize&levels=aaa)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
