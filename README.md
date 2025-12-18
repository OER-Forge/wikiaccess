# WikiAccess 📚

**Transform DokuWiki into Accessible WCAG 2.1 Compliant Documents**

WikiAccess converts DokuWiki pages into accessible HTML and Word documents with comprehensive accessibility testing, image processing, and broken link detection.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js & npm (for accessibility testing)
- Pandoc 2.9+

### Installation
```bash
# Clone and setup
git clone https://github.com/OER-Forge/wikiaccess.git
cd wikiaccess

python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
npm install pa11y
```

---

## 📋 Full Test Workflow

### **Step 1: Create URLS.txt**
Create a file named `URLS.txt` with one DokuWiki URL per line:
```
https://msuperl.org/wikis/pcubed/doku.php?id=183_notes:scalars_and_vectors
https://msuperl.org/wikis/pcubed/doku.php?id=183_notes:displacement_and_velocity
https://msuperl.org/wikis/pcubed/doku.php?id=183_notes:modeling_with_vpython
```

### **Step 2: Convert All Pages**
```bash
python3 convert_from_file_list.py
```

This will:
- ✅ Convert all URLs to HTML, DOCX, and Markdown
- 📥 Download all images with alt-text
- 📊 Test accessibility (WCAG 2.1 AA/AAA)
- 📁 Organize output in `output/` directory
- 📊 Generate initial reports

### **Step 3: Verify Conversion & Regenerate Reports**
```bash
python3 test_full_workflow.py
```

This will:
- 📊 Show database statistics (pages, images, broken links)
- 🔄 Regenerate all accessibility reports
- 📈 Show discovery workflow status
- 📁 List all generated output files

### **Step 4: Analyze Broken Links**
```bash
python3 test_broken_links.py
```

This will:
- 🔗 Identify broken internal wiki links
- 📊 Show which pages they're referenced on
- 💯 Rank broken links by frequency

### **Step 5: (Optional) Auto-Discover & Convert Missing Pages**
```bash
python3 wikiaccess/discovery_cli.py --auto-convert
```

This will:
- 🔍 Find all pages referenced by broken links
- ✅ Automatically convert them
- 🔄 Update broken link status in database

---

## 📁 Output Structure

```
output/
├── html/                    # Accessible HTML pages
├── docx/                    # Microsoft Word documents
├── markdown/                # Editable Markdown sources
├── images/                  # Downloaded media assets
├── reports/                 # Accessibility compliance reports
│   ├── index.html          # Hub with all reports
│   ├── accessibility_report.html      # WCAG 2.1 scores
│   ├── image_report.html              # Image analysis
│   ├── broken_links_report.html       # Broken links
│   └── [page]_accessibility.html      # Per-page reports
└── conversion_history.db    # SQLite database with all metadata
```

---

## 🗂️ Database Features

WikiAccess tracks all conversions in SQLite:

```sql
-- View database stats
sqlite3 output/conversion_history.db

-- Check page conversions
SELECT COUNT(*) FROM pages;

-- Check image downloads
SELECT status, COUNT(*) FROM images GROUP BY status;

-- Check link status
SELECT status, COUNT(*) FROM links GROUP BY status;
```

---

## 📊 Output Formats

### HTML
- Semantic HTML5 structure
- MathJax 3 equations
- Responsive design
- Dark mode support
- Interactive navigation

### Word (DOCX)
- Native OMML equations
- Embedded images
- Accessibility metadata
- Editable formatting
- Print-friendly layout

### Reports
- **Accessibility Dashboard**: WCAG 2.1 AA/AAA scores
- **Image Report**: Alt-text quality, download status, statistics
- **Broken Links Report**: Missing page references
- **Individual Page Reports**: Detailed accessibility issues per page

---

## 🎯 Key Features

### ♿ Accessibility Testing
- **WCAG 2.1 AA/AAA Compliance**: Powered by pa11y
- **Comprehensive Scoring**: 50+ accessibility rules
- **Interactive Reports**: Click-through dashboards with fix recommendations
- **Progress Tracking**: Historical trends and aggregate statistics

### 🖼️ Image Processing
- **Auto-Download**: Fetches all images from wiki
- **Alt-Text Extraction**: Preserves accessibility metadata
- **YouTube Support**: Auto-generates thumbnails
- **Status Tracking**: Identifies failed downloads
- **Analytics**: Reports image usage statistics

### 🔗 Link Management
- **Internal Link Resolution**: Converts wiki links to full URLs
- **Broken Link Detection**: Identifies pages not yet converted
- **Link Analytics**: Shows which pages are most referenced
- **Discovery Integration**: Suggests missing pages for conversion

### 📊 Database Tracking
- **Conversion History**: Complete audit trail
- **Incremental Updates**: Skips already-converted pages
- **Batch Management**: Track conversion runs
- **Statistics Export**: CSV reports for stakeholders

---

## 🔧 Advanced Usage

### Convert Single Page
```python
from wikiaccess import convert_wiki_page

result = convert_wiki_page(
    wiki_url="https://msuperl.org/wikis/pcubed",
    page_name="183_notes:scalars_and_vectors",
    output_dir="output"
)

print(f"HTML: {result['html_path']}")
print(f"WCAG AA Score: {result['aa_score']}%")
```

### Edit & Re-Convert (No Re-Scraping)
```bash
# Edit markdown
nano output/markdown/my_page.md

# Re-convert without fetching from wiki
python3 convert_from_markdown.py output/markdown/my_page.md
```

### Check Specific Page Accessibility
```bash
python3 -c "
from wikiaccess.database import ConversionDatabase
db = ConversionDatabase()
pages = db.get_all_pages_with_scores()
for p in pages:
    if 'scalars' in p['page_id']:
        print(f\"{p['page_id']}: AA={p['aa_score']}%, AAA={p['aaa_score']}%\")
"
```

---

## 📚 Documentation

- **[DATABASE.md](DATABASE.md)** - Database schema and queries
- **[docs/MODULE_DOCUMENTATION.md](docs/MODULE_DOCUMENTATION.md)** - Full API reference
- **[docs/ACCESSIBILITY_SCORING.md](docs/ACCESSIBILITY_SCORING.md)** - WCAG 2.1 details

---

## 🛠️ Technical Stack

- **Python**: BeautifulSoup4, python-docx, Pillow, requests
- **Accessibility**: pa11y engine (50+ WCAG rules)
- **Document Conversion**: Pandoc
- **Database**: SQLite3
- **Equations**: LaTeX → MathJax (HTML) / OMML (Word)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

**Made with ❤️ for accessible education and documentation**
