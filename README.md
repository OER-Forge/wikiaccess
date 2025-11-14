# WikiAccess 📚

**Transform DokuWiki into Accessible Documents**

WikiAccess converts DokuWiki pages into WCAG 2.1-compliant HTML and Microsoft Word documents with comprehensive accessibility testing powered by industry-standard tools.

---

## ✨ Features

### 🎯 **Multi-Format Output**
- **📄 Accessible HTML**: MathJax 3 equations, semantic HTML5, optimized contrast
- **📄 Microsoft Word**: Native OMML equations, embedded media, accessibility metadata
- **📱 Responsive Design**: Mobile-friendly HTML with dark mode support

### 🌐 **Content Processing**
- **Live Wiki Fetching**: Direct conversion from DokuWiki URLs (no API required)
- **📐 Advanced Equations**: LaTeX → MathJax (HTML) & OMML (Word) - fully editable
- **🖼️ Smart Media**: Auto-downloads images with alt-text, YouTube thumbnail generation
- **🔗 Link Resolution**: Converts internal wiki links to full URLs
- **📖 Markdown Pipeline**: Uses Markdown as intermediate format for reliability

### ♿ **Accessibility Excellence**
- **🏆 Industry-Standard Testing**: Powered by [pa11y](https://github.com/pa11y/pa11y) accessibility engine
- **📊 WCAG 2.1 Compliance**: AA and AAA level scoring with detailed feedback
- **🎯 Comprehensive Reports**: Interactive HTML dashboards with fix recommendations
- **🔍 50+ Accessibility Rules**: Color contrast, heading hierarchy, alt-text, keyboard access
- **📈 Progress Tracking**: Batch processing with aggregate compliance scores

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Node.js & npm (for accessibility testing)
- Pandoc 2.9+ (for document conversion)

### **Installation**
```bash
# Clone repository
git clone https://github.com/OER-Forge/wikiaccess.git
cd wikiaccess

# Set up environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install pa11y

# Install Pandoc
brew install pandoc  # macOS
# OR: sudo apt install pandoc  # Linux
# OR: Download from https://pandoc.org/installing.html  # Windows
```

### **Basic Usage**
```python
from wikiaccess import convert_wiki_page

# Convert single page
result = convert_wiki_page(
    wiki_url="https://your-wiki.com",
    page_name="namespace:page_name", 
    output_dir="output"
)

print(f"✓ HTML: {result['html_path']}")
print(f"✓ DOCX: {result['docx_path']}")
print(f"📊 Accessibility: {result['accessibility_report']}")
```

### **Batch Processing**
```bash
# Create URLS.txt with one URL per line
echo "https://your-wiki.com/doku.php?id=page1" > URLS.txt
echo "https://your-wiki.com/doku.php?id=page2" >> URLS.txt

# Convert all pages
python convert_from_file_list.py
```

---

## 📖 Core Functions

### **Primary Conversion Functions**

#### `convert_wiki_page(wiki_url, page_name, output_dir)`
Converts a single DokuWiki page to accessible HTML and DOCX formats.

**Parameters:**
- `wiki_url` (str): Base URL of DokuWiki site
- `page_name` (str): Page identifier (namespace:pagename format)
- `output_dir` (str): Output directory path

**Returns:** Dictionary with file paths and conversion statistics

#### `convert_multiple_pages(urls_and_pages, output_dir)`
Batch converts multiple pages with combined accessibility reporting.

**Parameters:**
- `urls_and_pages` (list): List of (wiki_url, page_name) tuples
- `output_dir` (str): Output directory path

**Returns:** Dictionary with batch processing results and aggregate reports

### **Utility Functions**

#### `convert_from_markdown.py`
Re-converts existing markdown files without re-scraping (for editing workflow).

#### `convert_from_file_list.py`
Processes URLS.txt file for batch conversion operations.

### **Module Architecture**

- **📡 `scraper.py`**: DokuWiki content fetching and media download
- **🔄 `parser.py`**: DokuWiki syntax parsing and content extraction  
- **📝 `markdown_converter.py`**: Markdown generation and Pandoc conversion
- **♿ `accessibility.py`**: pa11y-powered WCAG 2.1 compliance testing
- **📊 `reporting.py`**: Interactive dashboard and detailed report generation
- **🔧 `unified.py`**: High-level convenience functions
- **💻 `cli.py`**: Command-line interface

---

## 📁 Output Structure

WikiAccess creates a organized output directory:

```
output/
├── markdown/           📝 Editable Markdown sources
├── html/              🌐 Accessible HTML documents  
├── docx/              📄 Microsoft Word documents
├── images/            🖼️ Downloaded media assets
└── reports/           📊 Accessibility compliance reports
    ├── accessibility_report.html        # Dashboard
    └── page_accessibility.html          # Detailed reports
```

---

## 🧪 Example Workflows

### **Workflow 1: Full Conversion**
```bash
# Convert with full accessibility testing
python3 -c "
from wikiaccess import convert_wiki_page
result = convert_wiki_page(
    'https://physics.library.vsu.edu',
    '183_notes:scalars_and_vectors', 
    'output'
)
print(f'Accessibility Score: {result[\"accessibility_score\"]}%')
"
```

### **Workflow 2: Edit & Re-convert**
```bash
# Edit the markdown file
nano output/markdown/page_name.md

# Re-convert without re-scraping  
python convert_from_markdown.py output/markdown/page_name.md
```

### **Workflow 3: Batch Processing**
```bash
# Process 13 pages from URLS.txt
python convert_from_file_list.py

# View aggregate dashboard
open output/reports/accessibility_report.html
```

---

## 🎯 Accessibility Features

### **WCAG 2.1 Testing**
- **🔍 Comprehensive**: 50+ accessibility rules via pa11y
- **🎨 Color Contrast**: Real contrast ratios with fix recommendations
- **📋 Heading Structure**: Logical hierarchy validation
- **🖼️ Media Alt-text**: Image accessibility checking
- **⌨️ Keyboard Access**: Navigation and interaction testing

### **Scoring System**
- **AA Score**: WCAG 2.1 Level AA compliance (0-100%)
- **AAA Score**: WCAG 2.1 Level AAA compliance (0-100%)
- **Issue Details**: Element selectors and specific fix guidance
- **Progress Tracking**: Batch reports with aggregate statistics

### **Report Features**
- **📊 Interactive Dashboard**: Click-through navigation
- **🔗 Direct Links**: Access HTML/DOCX files from reports
- **📈 Statistics**: Success rates for images, equations, conversions
- **🎯 Actionable Feedback**: Specific WCAG guideline violations

---

## 📚 Documentation

### **Comprehensive Guides**
- **📘 [docs/README.md](docs/README.md)** - Complete documentation overview
- **🚀 [docs/QUICKSTART.md](docs/QUICKSTART.md)** - Installation and basic usage
- **📖 [docs/MODULE_DOCUMENTATION.md](docs/MODULE_DOCUMENTATION.md)** - Full API reference
- **♿ [docs/ACCESSIBILITY_SCORING.md](docs/ACCESSIBILITY_SCORING.md)** - How pa11y scoring works

### **Architecture Diagrams**
- **🏗️ [docs/ARCHITECTURE.png](docs/ARCHITECTURE.png)** - System components
- **🔄 [docs/WORKFLOWS.png](docs/WORKFLOWS.png)** - Conversion workflows  
- **📊 [docs/DATA_FLOW.png](docs/DATA_FLOW.png)** - Data transformations

---

## 🛠️ Technical Details

### **Dependencies**
- **Python**: beautifulsoup4, requests, python-docx, Pillow, latex2mathml
- **Node.js**: pa11y (accessibility testing)
- **External**: Pandoc (document conversion)

### **Supported Content**
- ✅ DokuWiki syntax (headings, lists, links, tables)
- ✅ LaTeX equations (`$inline$`, `$$display$$`)
- ✅ Images (PNG, JPG, GIF, SVG) with auto-download
- ✅ YouTube videos (iframe embed + thumbnail)
- ✅ Internal wiki links (auto-resolved to full URLs)
- ✅ Code blocks with syntax highlighting

### **Accessibility Standards**
- **WCAG 2.1**: Both AA and AAA compliance testing
- **pa11y Engine**: Industry-standard accessibility validation
- **HTML Standards**: Semantic HTML5, proper heading hierarchy
- **Document Standards**: Word accessibility metadata, alt-text

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)  
5. **Open** Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[pa11y](https://github.com/pa11y/pa11y)** - Accessibility testing engine
- **[Pandoc](https://pandoc.org/)** - Universal document converter
- **WCAG Guidelines** - Web Content Accessibility Guidelines 2.1

---

**Made with ❤️ for accessible education and documentation**