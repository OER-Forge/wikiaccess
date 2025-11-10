# WikiAccess - Usage Guide# WikiAccess - Usage Guide# WikiAccess - Usage Guide



**Transform DokuWiki into Accessible Documents**



## Overview**Transform DokuWiki into Accessible Documents****Transform DokuWiki into Accessible Documents**



WikiAccess converts DokuWiki pages to **both** accessible HTML and Word documents with comprehensive WCAG compliance reporting. No API configuration needed - works via HTTP with any DokuWiki instance.



## Installation## Overview## Overview



```bash

# Install the package

pip install -e .WikiAccess converts DokuWiki pages to **both** accessible HTML and Word documents with comprehensive WCAG compliance reporting. No API configuration needed - works via HTTP with any DokuWiki instance.WikiAccess converts DokuWiki pages to **both** accessible HTML and Word documents with comprehensive WCAG compliance reporting. No API configuration needed - works via HTTP with any DokuWiki instance.



# Or install from source

pip install -r requirements.txt

```## Quick Start## Quick Example



## Command Line Interface



### Basic Usage```bash```bash



```bash# Run the example conversion# Run the test conversion

# Convert a single page

wikiaccess https://your-wiki.com page:namepython test_dual_conversion.pypython test_dual_conversion.py



# Convert multiple pages

wikiaccess https://your-wiki.com page1 page2 page3

# Outputs:# Outputs:

# Specify output directory

wikiaccess https://your-wiki.com page:name -o my_output# - output/html/*.html (MathJax equations, embedded media)# - output/html/*.html (MathJax equations)



# HTML only# - output/docx/*.docx (OMML equations, embedded media)# - output/docx/*.docx (OMML equations)

wikiaccess https://your-wiki.com page:name -f html

# - output/accessibility_report.html (WCAG compliance dashboard)# - output/accessibility_report.html (compliance dashboard)

# DOCX only

wikiaccess https://your-wiki.com page:name -f docx``````



# Skip accessibility checking

wikiaccess https://your-wiki.com page:name --no-accessibility

```## Python API## Python API Usage



### Advanced CLI Options



```bash### Basic Dual-Format Conversion### Basic Dual-Format Conversion

# Multiple pages with custom output and formats

wikiaccess https://your-wiki.com page1 page2 \

  -o results \

  -f html docx \```python```python

  --no-accessibility

from scraper import DokuWikiHTTPClientfrom scraper import DokuWikiHTTPClient

# Get help

wikiaccess --helpfrom html_converter import HTMLConverterfrom html_converter import HTMLConverter



# Check versionfrom convert import EnhancedDokuWikiConverterfrom convert import EnhancedDokuWikiConverter

wikiaccess --version

```



## Python API# Initialize# Initialize



### High-Level API (Recommended)client = DokuWikiHTTPClient('https://your-wiki.com')client = DokuWikiHTTPClient('https://your-wiki.com')



```pythonhtml_conv = HTMLConverter(client)html_conv = HTMLConverter(client)

from wikiaccess import convert_wiki_page, convert_multiple_pages

docx_conv = EnhancedDokuWikiConverter(client)docx_conv = EnhancedDokuWikiConverter(client)

# Single page conversion

result = convert_wiki_page(

    wiki_url='https://your-wiki.com',

    page_name='page:name',# Convert single page# Convert to HTML

    output_dir='output',

    formats=['html', 'docx'],url = 'https://your-wiki.com/doku.php?id=your:page'url = 'https://your-wiki.com/doku.php?id=your:page'

    check_accessibility=True

)html_path, html_stats = html_conv.convert_url(url)



# Access results# HTML output# Output: output/html/your_page.html

print(f"HTML: {result['html']['file_path']}")

print(f"DOCX: {result['docx']['file_path']}")html_path, html_stats = html_conv.convert_url(url)

print(f"HTML WCAG AA: {result['accessibility']['html']['score_aa']}%")

print(f"Report: {result['accessibility_report']}")print(f"HTML: {html_path}")# Convert to Word



# Multiple pagesprint(f"Stats: {html_stats['images']} images, {html_stats['videos']} videos")docx_stats = docx_conv.convert_url(url, 'output/docx/your_page.docx')

results = convert_multiple_pages(

    wiki_url='https://your-wiki.com',# Output: output/docx/your_page.docx

    page_names=['page1', 'page2', 'page3'],

    output_dir='bulk_output'# Word output  ```

)

```docx_stats = docx_conv.convert_url(url, 'output/docx/your_page.docx')



### Modular API (Advanced)print(f"DOCX Stats: {docx_stats['images_success']}/{docx_stats['images_success'] + docx_stats['images_failed']} images")### With Accessibility Reporting



```python```

from wikiaccess import (

    DokuWikiHTTPClient,```python

    HTMLConverter,

    EnhancedDokuWikiConverter,### With Accessibility Reporting  "YOUR_URL" \

    AccessibilityChecker,

    ReportGenerator  -o output.docx \

)

```python  -u your_username \

# Initialize components

client = DokuWikiHTTPClient('https://your-wiki.com')from scraper import DokuWikiHTTPClient  -p your_password

html_converter = HTMLConverter(client)

word_converter = EnhancedDokuWikiConverter(client)from html_converter import HTMLConverter```



# Convert to HTMLfrom convert import EnhancedDokuWikiConverter

url = 'https://your-wiki.com/doku.php?id=page:name'

html_path, html_stats = html_converter.convert_url(url)from a11y_checker import AccessibilityChecker## Without Embedding Media (faster)

print(f"✅ HTML saved: {html_path}")

print(f"📊 Images: {html_stats['images_success']}/{html_stats['images_total']}")from reporter import ReportGenerator```bash



# Convert to Wordpython convert.py \

word_stats = word_converter.convert_url(url, 'output.docx')

print(f"📊 Equations: {word_stats['equations_total']}")# Setup  "YOUR_URL" \



# Check accessibilityclient = DokuWikiHTTPClient('https://your-wiki.com')  -o output.docx \

checker = AccessibilityChecker()

html_report = checker.check_html(html_path)html_conv = HTMLConverter(client)  --no-images \

word_report = checker.check_docx('output.docx')

docx_conv = EnhancedDokuWikiConverter(client)  --no-videos

print(f"HTML WCAG AA: {html_report['score_aa']}%")

print(f"Word WCAG AA: {word_report['score_aa']}%")checker = AccessibilityChecker()```



# Generate reportsreporter = ReportGenerator('output')

reporter = ReportGenerator('output')

reporter.add_page_reports('page_name', html_report, word_report, html_stats, word_stats)## What Gets Converted

dashboard = reporter.generate_dashboard()

print(f"📊 Dashboard: {dashboard}")# Convert

```

url = 'https://your-wiki.com/doku.php?id=page:name'✅ **Text Formatting:**

## Examples

page_name = 'page_name'- Headings (all levels)

### Example 1: Educational Content

- Bold, italic, underline

```python

from wikiaccess import convert_wiki_pagehtml_path, html_stats = html_conv.convert_url(url)- Lists (bullet points)



# Convert a physics course pagedocx_stats = docx_conv.convert_url(url, f'output/docx/{page_name}.docx')- Line breaks

result = convert_wiki_page(

    wiki_url='https://physics-wiki.edu',

    page_name='mechanics:vectors',

    output_dir='physics_output'# Check accessibility✅ **Media:**

)

html_report = checker.check_html(html_path)- Images (downloaded and embedded with alt-text)

# Results include equations, images, videos

print(f"Converted with {result['html']['stats']['equations_total']} equations")docx_report = checker.check_docx(f'output/docx/{page_name}.docx')- YouTube videos (thumbnail + clickable link)

```

- Image captions

### Example 2: Documentation Site

# Generate reports

```bash

# Convert entire documentation sectionreporter.add_page_reports(page_name, html_report, docx_report, ✅ **Links:**

wikiaccess https://docs.company.com \

  introduction \                         html_stats, docx_stats)- External links (to Wikipedia, etc.)

  getting-started \

  advanced-usage \reporter.generate_detailed_reports()- Internal wiki links (converted to full URLs)

  api-reference \

  -o company-docsdashboard_path = reporter.generate_dashboard()- All links are accessible with descriptive text

```



### Example 3: Accessibility Audit

print(f"\nAccessibility Dashboard: {dashboard_path}")✅ **Equations:**

```python

from wikiaccess import convert_multiple_pagesprint(f"HTML WCAG AA: {html_report['score_aa']}%")- LaTeX equations (rendered as formatted text)



# Convert and audit multiple pagesprint(f"DOCX WCAG AA: {docx_report['score_aa']}%")- Both inline and block equations

results = convert_multiple_pages(

    wiki_url='https://corporate-wiki.com',```

    page_names=['policy1', 'policy2', 'guidelines'],

    check_accessibility=True✅ **Accessibility:**

)

### Batch Conversion- Document title and language

# Check compliance scores

for page, result in results.items():- Proper heading hierarchy

    if 'accessibility' in result:

        html_score = result['accessibility']['html']['score_aa']```python- Alt text for all images and videos

        word_score = result['accessibility']['docx']['score_aa']

        print(f"{page}: HTML={html_score}%, Word={word_score}%")from scraper import DokuWikiHTTPClient- Semantic document structure

```

from html_converter import HTMLConverter- Screen reader compatible

## Output Structure

from convert import EnhancedDokuWikiConverter

```

output/from a11y_checker import AccessibilityChecker## Batch Convert Multiple Pages

├── accessibility_report.html          # Main dashboard

├── page_name_accessibility.html       # Detailed page reportfrom reporter import ReportGenerator

├── html/

│   ├── page_name.html                 # Accessible HTMLCreate a simple script:

│   └── images/                        # Downloaded images

└── docx/# Pages to convert

    └── page_name.docx                 # Accessible Word document

```pages = [```bash



## Configuration    ('183_notes:scalars_and_vectors', 'Scalars and Vectors'),#!/bin/bash



### Environment Variables    ('183_notes:momentum', 'Momentum Principle'),# convert_all.sh



```bash    ('183_notes:energy', 'Energy Principle'),

# Optional: Set default output directory

export WIKIACCESS_OUTPUT_DIR="/path/to/default/output"]# List of pages to convert



# Optional: Set timeout for downloadspages=(

export WIKIACCESS_TIMEOUT=30

```# Initialize  "183_notes:scalars_and_vectors"



### Python Configurationwiki_url = 'https://your-wiki.com'  "183_notes:momentum"



```pythonclient = DokuWikiHTTPClient(wiki_url)  "183_notes:energy"

# Configure timeouts and retries

from wikiaccess import DokuWikiHTTPClienthtml_conv = HTMLConverter(client)  "183_notes:forces"



client = DokuWikiHTTPClient(docx_conv = EnhancedDokuWikiConverter(client))

    'https://your-wiki.com',

    timeout=30,checker = AccessibilityChecker()

    max_retries=3

)reporter = ReportGenerator('output')BASE_URL="https://msuperl.org/wikis/pcubed/doku.php?id="

```



## Troubleshooting

# Convert all pagesfor page in "${pages[@]}"; do

### Common Issues

for page_id, title in pages:  echo "Converting: $page"

1. **Missing Images**: Some wikis restrict image downloads

   - Solution: Images are referenced in output with original URLs    print(f"\nConverting: {title}")  filename=$(echo "$page" | tr ':' '_')



2. **Equation Rendering**: Complex LaTeX may not convert perfectly    url = f'{wiki_url}/doku.php?id={page_id}'  python convert.py "${BASE_URL}${page}" -o "output/${filename}.docx"

   - Solution: Check the equation conversion logs

    page_name = page_id.replace(':', '_')done

3. **Accessibility Scores**: Low scores indicate WCAG issues

   - Solution: Review the detailed accessibility report    



### Debug Mode    # Convertecho "Done!"



```python    html_path, html_stats = html_conv.convert_url(url, title)```

# Enable verbose logging

import logging    docx_stats = docx_conv.convert_url(url, f'output/docx/{page_name}.docx', title)

logging.basicConfig(level=logging.DEBUG)

    Make it executable and run:

# Then run your conversion

from wikiaccess import convert_wiki_page    # Check```bash

result = convert_wiki_page(...)

```    html_report = checker.check_html(html_path)chmod +x convert_all.sh



### Getting Help    docx_report = checker.check_docx(f'output/docx/{page_name}.docx')./convert_all.sh



- Check the generated accessibility reports for specific issues    ```

- Review the console output for conversion statistics

- Use `wikiaccess --help` for CLI options    # Add to reporter

- Check the detailed logs in debug mode

    reporter.add_page_reports(page_name, html_report, docx_report,## Troubleshooting

## Next Steps

                             html_stats, docx_stats)

- See [ACCESSIBILITY.md](ACCESSIBILITY.md) for WCAG compliance details

- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical implementation### "Could not download" warnings

- See [PACKAGE_STRUCTURE.md](PACKAGE_STRUCTURE.md) for development setup
# Generate combined reportsSome images might not be publicly accessible or the path format is different. The converter will add a text reference instead.

reporter.generate_detailed_reports()

dashboard = reporter.generate_dashboard()### "Authentication required"

print(f"\n✓ Dashboard: {dashboard}")Add username and password:

``````bash

python convert.py "URL" -o output.docx -u USERNAME -p PASSWORD

## What Gets Converted```



### ✅ Text Formatting### Images not showing

- **Headings**: All levels (H1-H5)Check if the image paths in your DokuWiki are correct. You can test image download with the scraper test:

- **Styles**: Bold, italic, underline```bash

- **Lists**: Bullet pointspython scraper.py "YOUR_PAGE_URL"

- **Paragraphs**: With proper spacing```



### ✅ Equations## Check Accessibility

- **HTML**: MathJax 3 rendering (inline `\(...\)` and display `\[...\]`)

- **Word**: Native OMML objects (editable in Word's equation editor)After conversion:

- **Support**: Fractions, superscripts, subscripts, vectors, Greek letters

1. **Open in Word**

### ✅ Media   ```bash

- **Images**: Downloaded and embedded with alt-text   open output/your_file.docx

- **YouTube**: HTML iframes, Word thumbnails with links   ```

- **Statistics**: Success/failure tracking per media item

2. **Run Accessibility Checker**

### ✅ Links   - File → Info → Check for Issues → Check Accessibility

- **External**: Direct links to websites

- **Internal**: Wiki links converted to full URLs3. **Test with Screen Reader**

- **Accessible**: Descriptive text (not "click here")   - macOS: Press `Cmd+F5` for VoiceOver

   - Windows: Use NVDA (free)

### ✅ Accessibility

- **WCAG 2.1 AA**: Primary target## CLI Options Reference

- **WCAG 2.1 AAA**: Stretch goal

- **Features**: ```

  - Document title and languageusage: convert.py [-h] -o OUTPUT [-u USERNAME] [-p PASSWORD] [-t TITLE] 

  - Proper heading hierarchy                 [-l LANGUAGE] [--no-images] [--no-videos] [--temp-dir TEMP_DIR]

  - Alt text for images                 url

  - Semantic structure

  - Screen reader compatibleArguments:

  url                   DokuWiki page URL to convert

## Output Structure  -o, --output         Output Word document path (required)

  -u, --username       DokuWiki username (if auth required)

```  -p, --password       DokuWiki password (if auth required)

output/  -t, --title          Document title (for accessibility)

├── html/  -l, --language       Document language (default: en-US)

│   ├── page_name.html       # Accessible HTML with MathJax  --no-images          Do not embed images

│   └── images/  --no-videos          Do not embed video thumbnails

│       └── *.png            # Downloaded images  --temp-dir           Temporary directory for downloads

├── docx/```

│   └── page_name.docx       # Word with OMML equations

├── accessibility_report.html # Dashboard with all pages## Success! 🎉

└── page_name_accessibility.html # Detailed per-page report

```Your DokuWiki pages are now being converted to fully accessible Word documents with:

- ✅ Embedded images with alt-text

## Authentication- ✅ YouTube video thumbnails with links  

- ✅ All formatting preserved

For wikis requiring login:- ✅ Internal links resolved

- ✅ Full WCAG 2.1 AA accessibility compliance

```python

client = DokuWikiHTTPClient(Need help? Check the full documentation in `README.md` or `ARCHITECTURE_PROPOSAL.md`.

    'https://your-wiki.com',
    username='your_username',
    password='your_password'
)
```

## Advanced Options

### Disable Media Embedding

```python
# HTML converter
html_conv.convert_url(url)  # Always embeds media

# DOCX converter
docx_conv.convert_url(
    url, 
    output_path,
    embed_images=False,  # Skip image downloads
    embed_videos=False   # Skip video thumbnails
)
```

### Custom Output Directories

```python
html_conv = HTMLConverter(client, output_dir='custom_html')
docx_conv = EnhancedDokuWikiConverter(client, temp_dir='custom_temp')
reporter = ReportGenerator('custom_reports')
```

### Custom Document Metadata

```python
docx_conv.convert_url(
    url,
    output_path,
    document_title='Custom Title',  # For accessibility
    language='en-US'                # Document language
)
```

## Accessibility Reports

Reports show:

### Dashboard View
- **Overall scores**: WCAG AA/AAA percentages
- **Format comparison**: HTML vs DOCX side-by-side
- **Media statistics**: Images/videos/equations success rates
- **File links**: Direct access to converted files

### Detailed Per-Page Reports
- **Conversion statistics**: Media embedding results
- **WCAG issues**: Specific problems found
- **Issue severity**: AA vs AAA level
- **Recommendations**: How to fix issues

### Interpreting Scores

- **90-100%**: Excellent - Minor issues only
- **70-89%**: Good - Some improvements needed
- **50-69%**: Fair - Significant issues to address
- **<50%**: Poor - Major accessibility problems

### Common Issues

| Issue | WCAG Level | How to Fix |
|-------|------------|------------|
| Heading hierarchy skip | AA | Use sequential heading levels (H1→H2→H3) |
| Missing alt text | AA | Add descriptions to images in source wiki |
| Low color contrast | AA | Use high contrast colors in styling |
| Complex language | AAA | Simplify wording, add glossary |

## Troubleshooting

### Images Not Downloading

**Problem**: `⚠ Could not download: image.png`

**Solutions**:
1. Check image permissions on wiki
2. Verify image path is correct
3. Check if authentication is needed
4. Image may be restricted (403 Forbidden)

### Equations Not Converting

**Problem**: Equations show as text

**Solutions**:
1. Verify LaTeX syntax is valid
2. Check for unsupported LaTeX commands
3. Test with simpler equations first
4. See OMML_IMPLEMENTATION.md for supported features

### Low Accessibility Scores

**Problem**: WCAG scores below 70%

**Solutions**:
1. Check heading hierarchy in source wiki
2. Add alt text to images
3. Use descriptive link text
4. Review detailed report for specific issues

## Performance Tips

1. **Batch conversions**: Reuse client/converter objects
2. **Skip media**: Set `embed_images=False` for faster conversion
3. **Local temp**: Use SSD for temp_dir
4. **Parallel processing**: Convert different pages in parallel (separate processes)

## Next Steps

- Review [ACCESSIBILITY.md](ACCESSIBILITY.md) for WCAG compliance testing
- See [OMML_IMPLEMENTATION.md](OMML_IMPLEMENTATION.md) for equation details
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for module structure
- Read [QUICKSTART.md](QUICKSTART.md) for 5-minute intro

---

**WikiAccess** - Making documentation accessible to everyone
