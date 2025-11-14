# WikiAccess Module Documentation

## Overview

WikiAccess is a comprehensive toolkit for converting DokuWiki pages into WCAG 2.1-compliant accessible HTML and Word documents. The system uses Markdown as an intermediate format to simplify the conversion pipeline.

**Version**: 2.0.0  
**Architecture**: Markdown-based (DokuWiki → Markdown → HTML/DOCX via Pandoc)

## System Architecture

![System Architecture Diagram](ARCHITECTURE.png)

![Data Flow Diagram](DATA_FLOW.png)

---

## Core Modules

### 1. `scraper.py` - DokuWikiHTTPClient

**Purpose**: Fetch content from DokuWiki sites and download media assets.

**Key Classes**:
- `DokuWikiHTTPClient`: HTTP client for DokuWiki interaction

**Key Methods**:
- `get_page_from_url(url)` - Fetch raw DokuWiki syntax from a page
- `download_media(media_path, save_path)` - Download images/media files
- `resolve_internal_link(page_id, context)` - Convert internal wiki links to full URLs

**Example**:
```python
from wikiaccess import DokuWikiHTTPClient

client = DokuWikiHTTPClient("https://your-wiki.com")
page_id, content = client.get_page_from_url("https://your-wiki.com/doku.php?id=page:name")
client.download_media("image:name.png", "output/images/name.png")
```

---

### 2. `parser.py` - DokuWikiParser & AccessibilityManager

**Purpose**: Parse DokuWiki syntax into Markdown and track accessibility hints.

**Key Classes**:
- `DokuWikiParser`: Parses DokuWiki syntax line-by-line
- `AccessibilityManager`: Manages accessibility metadata and hints
- `DokuWikiToWordConverter`: Legacy (deprecated)

**Key Methods**:
- `parse_line(line)` - Parse a single DokuWiki line, returns `{type, level, content}`
- `parse_inline_formatting(text)` - Extract bold, italic, links, equations from text
- `set_accessibility_hint(key, value)` - Store accessibility metadata

**Line Types**:
- `heading` - Headings with level (1-6)
- `paragraph` - Regular text
- `list_item` - Bullet points
- `image` - Images/videos/embeds
- `youtube` - YouTube videos
- `equation_block` - Display math ($$...$$)
- `equation_inline` - Inline math ($...$)
- `empty` - Blank lines
- `code_block` - Code blocks

**Example**:
```python
from wikiaccess import DokuWikiParser

parser = DokuWikiParser()
result = parser.parse_line("== Section Title ==")
# Returns: {type: 'heading', level: 2, content: 'Section Title'}

elements = parser.parse_inline_formatting("This is **bold** and //italic//")
# Returns: [(text, {...}), (bold, {...}), (text, {...}), (italic, {...})]
```

---

### 3. `markdown_converter.py` - MarkdownConverter

**Purpose**: Convert DokuWiki content to Markdown, then use Pandoc to generate HTML/DOCX.

**Key Classes**:
- `MarkdownConverter`: Main converter orchestrating DokuWiki → Markdown → HTML/DOCX

**Key Methods**:
- `convert_url(url)` - Fetch and convert a DokuWiki page URL
- `_convert_to_markdown(content, title)` - Parse DokuWiki syntax to Markdown
- `_process_inline(text)` - Handle inline formatting (bold, italic, links, equations)
- `_process_image(parsed)` - Download images and create references
- `_pandoc_convert(md_path, output_path, format_type)` - Use Pandoc for conversion
- `_enhance_html_accessibility(html_path)` - Add CSS and MathJax to HTML

**Output Structure**:
```
output/
├── markdown/           # Markdown source files (editable)
│   ├── page1.md
│   └── page2.md
├── images/            # Downloaded images and YouTube thumbnails
│   ├── image1.png
│   ├── image2.jpg
│   └── youtube_[id].jpg
├── html/              # Generated HTML files
│   ├── page1.html
│   └── page2.html
├── docx/              # Generated Word documents
│   ├── page1.docx
│   └── page2.docx
└── reports/           # Accessibility reports
    ├── accessibility_report.html
    ├── page1_accessibility.html
    └── page2_accessibility.html
```

**Image Handling**:
- Regular images: Downloaded to `output/images/`, referenced as `images/filename.png` in markdown
- YouTube videos: Thumbnail fetched as `youtube_[id].jpg`, creates clickable link to video
- Pandoc resolves relative paths using `--resource-path`

**Equation Handling**:
- Inline math: `$...$` → MathJax rendered in HTML, OMML in DOCX
- Display math: `$$...$$` → Block-level MathJax in HTML, OMML in DOCX

**Example**:
```python
from wikiaccess import MarkdownConverter, DokuWikiHTTPClient

client = DokuWikiHTTPClient("https://your-wiki.com")
converter = MarkdownConverter(client, "output")
html_path, docx_path, stats = converter.convert_url("https://your-wiki.com/doku.php?id=page:name")
print(f"Generated: {html_path}, {docx_path}")
print(f"Images: {stats['images_success']}/{stats['images']}")
```

---

### 4. `accessibility.py` - AccessibilityChecker

**Purpose**: Validate HTML and DOCX against WCAG 2.1 AA and AAA standards.

**Key Classes**:
- `AccessibilityChecker`: Main checker for accessibility compliance
- `AccessibilityReport`: Data structure for holding check results

**Key Methods**:
- `check_html(html_path)` - Validate HTML file
- `check_docx(docx_path)` - Validate Word document
- `_check_headings()` - Verify proper heading hierarchy
- `_check_contrast()` - Check color contrast (AA/AAA)
- `_check_images()` - Validate alt text, extract image filenames
- `_check_links()` - Check link text and targets
- `_check_equations()` - Verify equation accessibility
- `_check_videos()` - Check video descriptions
- `_check_color_dependence()` - Ensure information not conveyed by color alone

**Report Format**:
```python
{
    'aa_issues': [
        {
            'type': 'missing_alt_text',
            'element': 'Image: image1.png',
            'suggestion': 'Add descriptive alt text'
        }
    ],
    'aaa_issues': [...],
    'aa_score': 85,  # percentage
    'aaa_score': 65,
    'images': {'total': 10, 'with_alt': 9},
    'videos': {'total': 2, 'with_captions': 0}
}
```

**Example**:
```python
from wikiaccess import AccessibilityChecker

checker = AccessibilityChecker()
html_report = checker.check_html("output/html/page.html")
docx_report = checker.check_docx("output/docx/page.docx")

print(f"HTML AA Score: {html_report['aa_score']}%")
print(f"DOCX AAA Score: {docx_report['aaa_score']}%")
```

---

### 5. `reporting.py` - ReportGenerator

**Purpose**: Generate accessible HTML dashboards and detailed accessibility reports.

**Key Classes**:
- `ReportGenerator`: Creates HTML reports and dashboards

**Key Methods**:
- `add_page_reports(page_name, html_report, docx_report, html_stats, docx_stats)` - Add results for a page
- `generate_dashboard()` - Create combined dashboard HTML
- `generate_detailed_reports()` - Create per-page detail reports

**Report Types**:
1. **Dashboard** (`accessibility_report.html`): Overview of all pages
   - Summary statistics (AA/AAA scores)
   - Page-by-page comparison table
   - Links to detail reports and converted files

2. **Detail Report** (`page_name_accessibility.html`): Individual page analysis
   - Specific issues found (with suggestions)
   - Image analysis with filenames
   - Video and equation statistics
   - Links to HTML/DOCX versions

**Example**:
```python
from wikiaccess import ReportGenerator

reporter = ReportGenerator("output/reports")
reporter.add_page_reports(
    "page1",
    html_report={'aa_issues': [...], 'aa_score': 85},
    docx_report={'aa_issues': [...], 'aa_score': 90},
    html_stats={'images': 5},
    docx_stats={'images': 5}
)
reporter.generate_detailed_reports()
dashboard = reporter.generate_dashboard()
```

---

### 6. `unified.py` - High-Level Convenience Functions

**Purpose**: Provide simple interfaces for common conversion tasks.

**Key Functions**:
- `convert_wiki_page(wiki_url, page_name, output_dir, formats, check_accessibility)` - Convert single page
- `convert_multiple_pages(wiki_url, page_names, output_dir, formats, check_accessibility)` - Batch convert

**Example**:
```python
from wikiaccess import convert_multiple_pages

results = convert_multiple_pages(
    wiki_url="https://your-wiki.com",
    page_names=["page:one", "page:two"],
    output_dir="output",
    check_accessibility=True
)

for page, result in results.items():
    print(f"{page}: {result['html']['file_path']}")
```

---

### 7. `cli.py` - Command-Line Interface

**Purpose**: Provide command-line access to conversion functions.

**Commands**:
```bash
# Convert single page
python -m wikiaccess convert https://wiki.com page:name

# Convert multiple pages
python -m wikiaccess batch-convert https://wiki.com page:one page:two page:three

# Convert from file list
python convert_from_file_list.py

# Convert from markdown (no scraping)
python convert_from_markdown.py
```

---

## Workflows

### Workflow 1: Full Conversion (Scrape + Convert + Check)

![Full Conversion Workflow](WORKFLOWS.png)

```
1. DokuWiki scraper.py: Fetch page content
2. parser.py: Parse DokuWiki syntax
3. markdown_converter.py: Generate Markdown
4. Pandoc (external): Convert to HTML/DOCX
5. accessibility.py: Check compliance
6. reporting.py: Generate reports
```

**Entry Point**: `convert_wiki_page()` or `convert_multiple_pages()`

### Workflow 2: Edit + Re-convert (No Scraping)

```
1. User edits output/markdown/page.md
2. convert_from_markdown.py: Read markdown
3. markdown_converter.py: Pandoc conversion
4. accessibility.py: Check compliance
5. reporting.py: Generate reports
```

**Entry Point**: `python convert_from_markdown.py [files...]`

### Workflow 3: Batch Processing

```
1. Read URLS.txt (one URL per line)
2. Loop: Workflow 1 for each URL
3. Single combined accessibility dashboard
```

**Entry Point**: `python convert_from_file_list.py`

---

## Configuration

### Environment Variables
- `WIKIACCESS_OUTPUT_DIR` - Default output directory (default: `output/`)
- `WIKIACCESS_CHECK_ACCESSIBILITY` - Enable/disable checks (default: `true`)

### Markdown Conventions

The system expects standard Markdown with these extensions:

**Math**:
```markdown
Inline: $E = mc^2$
Display: $$ \int_0^\infty e^{-x} dx = 1 $$
```

**Images**:
```markdown
![alt text](images/filename.png)
[![Click to video](images/youtube_[id].jpg)](https://youtube.com/watch?v=[id])
```

**Internal Links**:
```markdown
[Link text](https://wiki.com/doku.php?id=page:name)
```

---

## Accessibility Checks

### WCAG 2.1 AA (Minimum)
- ✓ Heading hierarchy (H1 → H2 → H3)
- ✓ Image alt text
- ✓ Color contrast (4.5:1 for text)
- ✓ Link text description
- ✓ Form labels
- ✓ Video captions
- ✓ Equation accessibility

### WCAG 2.1 AAA (Enhanced)
- ✓ Color contrast (7:1 for text)
- ✓ Extended descriptions for complex images
- ✓ Sign language for videos
- ✓ Full text alternatives for audio

---

## Dependencies

- **Python 3.8+**
- **Pandoc** (external tool, required)
  - macOS: `brew install pandoc`
  - Linux: `apt-get install pandoc`
  - Windows: Download from https://pandoc.org/installing.html

- **Python Packages**:
  - `requests` - HTTP client for scraping
  - `python-docx` - Word document creation/analysis
  - `beautifulsoup4` - HTML parsing
  - `lxml` - XML/HTML processing

---

## Example: Complete Workflow

```python
from wikiaccess import convert_multiple_pages

# Convert 3 pages from wiki
results = convert_multiple_pages(
    wiki_url="https://physics-wiki.edu",
    page_names=[
        "course:physics:mechanics",
        "course:physics:waves",
        "course:physics:optics"
    ],
    output_dir="output",
    check_accessibility=True
)

# Edit markdown if needed
# output/markdown/course_physics_mechanics.md
# ... make edits ...

# Re-convert without scraping
from wikiaccess.markdown_converter import MarkdownConverter
from wikiaccess.scraper import DokuWikiHTTPClient

client = DokuWikiHTTPClient("https://physics-wiki.edu")
converter = MarkdownConverter(client, "output")
html, docx, stats = converter.convert_url("dummy", "course:physics:mechanics")

# Check results
for page, result in results.items():
    print(f"\n{page}:")
    print(f"  HTML: {result['html']['file_path']}")
    print(f"  DOCX: {result['docx']['file_path']}")
    print(f"  Accessibility: {result['accessibility']}")
```

---

## Troubleshooting

### Pandoc not found
```
Error: Pandoc is not installed
Solution: brew install pandoc
```

### Images not showing in HTML
- Check: `output/images/` directory exists and contains images
- Check: Image paths in markdown are relative: `images/filename.png`
- Check: HTML file is in `output/html/` (correct relative path: `../images/`)

### Equations not rendering
- Check: HTML has MathJax script tag
- Check: Equations in markdown use `$...$` (inline) or `$$...$$` (display)
- Clear browser cache if equations don't update

### Word documents missing images
- Pandoc handles image embedding from `--resource-path`
- Check: Images exist in `output/images/`
- Note: DOCX has more restrictions than HTML for image formats

---

## Performance Notes

- **Scraping**: ~5-10 seconds per page (network dependent)
- **Conversion**: ~1-2 seconds per page (Pandoc + accessibility checks)
- **Batch**: 13 pages ≈ 2-3 minutes total
- **Re-conversion** (markdown only): ~0.5 seconds per page

---

## Future Improvements

1. **PDF Export**: Add PDF generation via Pandoc
2. **EPUB**: E-book format support
3. **LaTeX**: Direct LaTeX source generation
4. **Custom CSS**: User-provided stylesheets
5. **Parallel Processing**: Multi-threaded batch conversion
6. **Caching**: Skip unchanged pages in batch mode
7. **Interactive Dashboard**: Real-time accessibility checking UI

