# WikiAccess Documentation

This folder contains comprehensive documentation for the WikiAccess module and system.

## Files

### 1. **QUICKSTART.md** - Start Here!
Quick reference guide for getting up and running:
- Installation instructions
- Basic usage examples
- Common tasks
- Troubleshooting tips

**Read this first if you're new to WikiAccess.**

### 2. **MODULE_DOCUMENTATION.md** - Complete API Reference
Comprehensive documentation of all modules and functions:
- **Core Modules**: scraper, parser, markdown_converter, accessibility, reporting, unified, cli
- **Key Classes & Methods**: Detailed signatures and descriptions
- **Workflows**: Full conversion pipeline, edit-and-convert workflow, batch processing
- **Configuration**: Environment variables and conventions
- **WCAG Checks**: What accessibility standards are checked
- **Dependencies**: Required packages and external tools

**Read this to understand the system deeply and integrate WikiAccess into your code.**

### 3. **ACCESSIBILITY_SCORING.md** - Accessibility Scoring System
Comprehensive documentation of how WCAG 2.1 compliance scores are calculated:
- **Scoring Methodology**: Pass/fail ratio calculations for AA and AAA scores
- **HTML Tests**: 11 accessibility checks with detailed explanations
- **DOCX Tests**: 5 document accessibility validations  
- **Score Interpretation**: What different score ranges mean
- **WCAG Standards**: Complete mapping to WCAG 2.1 guidelines
- **Limitations**: Understanding what automated testing can and cannot detect

**Read this to understand precisely how accessibility scores are computed.**

### 4. **ARCHITECTURE.d2** - System Architecture Diagram
D2 language diagram showing:
- System components (Scraper, Parser, Converter, Checker, Reporter)
- Data flow between modules
- Storage locations
- Input/output relationships

![System Architecture](ARCHITECTURE.png)

**Visualize the component relationships and data flow.**

### 5. **WORKFLOWS.d2** - Conversion Workflows Diagram
D2 language diagram showing three workflows:
1. **Workflow 1**: Full DokuWiki conversion (scrape → parse → convert → check)
2. **Workflow 2**: Edit markdown and re-convert (no scraping)
3. **Workflow 3**: Batch process multiple pages

![Conversion Workflows](WORKFLOWS.png)

**Understand the step-by-step process for each use case.**

### 6. **DATA_FLOW.d2** - Data Transformation Diagram
D2 language diagram showing:
- Input sources
- Data transformation through each phase
- Intermediate formats
- Final output structure

![Data Flow](DATA_FLOW.png)

**See how data is transformed at each stage of the pipeline.**

## Viewing D2 Diagrams

The `.d2` files are text-based diagrams that can be viewed/edited using:

### Online (Recommended)
1. Go to https://d2lang.com/play
2. Copy-paste the content of any `.d2` file
3. View the rendered diagram

### Command Line
```bash
# Install D2
# macOS:
brew install d2

# Linux:
curl -fsSL https://d2lang.com/install.sh | sh -s --

# Then render:
d2 ARCHITECTURE.d2 ARCHITECTURE.svg
d2 WORKFLOWS.d2 WORKFLOWS.svg
d2 DATA_FLOW.d2 DATA_FLOW.svg

# View in browser:
open ARCHITECTURE.svg
```

### VS Code Extension
1. Install the "D2" extension by Terrastruct
2. Open any `.d2` file
3. Diagrams render in VS Code preview

## Getting Started

1. **New to WikiAccess?**
   - Start with `QUICKSTART.md`
   - Install and run a basic example

2. **Want to understand the system?**
   - Read `MODULE_DOCUMENTATION.md` overview section
   - View `ARCHITECTURE.d2` and `WORKFLOWS.d2` diagrams
   - Review specific module documentation

3. **Integrating WikiAccess into your project?**
   - Read `MODULE_DOCUMENTATION.md` completely
   - Review the "Example: Complete Workflow" section
   - Check relevant module API reference

4. **Troubleshooting issues?**
   - Check `QUICKSTART.md` troubleshooting section
   - Review `DATA_FLOW.d2` to understand where the issue might be
   - Check module source code (well-commented)

## Documentation Structure

```
docs/
├── README.md (this file)
├── QUICKSTART.md              ← Start here
├── MODULE_DOCUMENTATION.md    ← Full reference
├── ARCHITECTURE.d2            ← Component diagram
├── WORKFLOWS.d2               ← Process flows
└── DATA_FLOW.d2               ← Data transformation
```

## Key Concepts

### Workflows

**Workflow 1: Full Conversion**
```
DokuWiki URL → Scraper → Parser → Markdown → Pandoc → HTML/DOCX → Check → Report
```

**Workflow 2: Edit & Re-convert**
```
Edit Markdown → Pandoc → HTML/DOCX → Check → Report
```

**Workflow 3: Batch Processing**
```
URL List → Loop Workflow 1 for each URL → Combined Report
```

### Output Structure

```
output/
├── markdown/      ← Editable source
├── images/        ← Downloaded assets + thumbnails
├── html/          ← Generated HTML files
├── docx/          ← Generated Word documents
└── reports/       ← Accessibility reports
```

### Key Features

- ✅ Converts DokuWiki pages to accessible HTML and Word documents
- ✅ Uses Markdown as intermediate format (simple, editable)
- ✅ Checks WCAG 2.1 AA and AAA compliance
- ✅ Generates accessibility dashboards and reports
- ✅ Supports batch processing
- ✅ Re-conversion without scraping (edit → convert workflow)
- ✅ Handles equations (LaTeX → MathJax in HTML, OMML in DOCX)
- ✅ Downloads images and YouTube thumbnails

## Common Questions

**Q: How do I fix accessibility issues?**
A: Edit the markdown file (images/equations/formatting), then re-convert without scraping.

**Q: Can I use my own CSS?**
A: Yes, customize the CSS in `markdown_converter.py`'s `_enhance_html_accessibility()` method.

**Q: What if images don't show in HTML?**
A: Check that images are in `output/images/` and markdown references them correctly.

**Q: How do I process multiple pages?**
A: Create `URLS.txt` with one URL per line, then run `python convert_from_file_list.py`.

**Q: Can I convert without Pandoc?**
A: No, Pandoc is required for HTML/DOCX generation. Install it first.

## Contributing

When updating documentation:
1. Keep `QUICKSTART.md` concise and example-focused
2. Update `MODULE_DOCUMENTATION.md` for API changes
3. Update `.d2` diagrams if architecture changes
4. Ensure examples are runnable and tested

## Version

- WikiAccess Version: 2.0.0
- Architecture: Markdown-based (DokuWiki → Markdown → HTML/DOCX via Pandoc)
- Last Updated: November 2025

