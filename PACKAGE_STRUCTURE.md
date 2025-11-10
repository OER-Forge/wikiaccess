# WikiAccess Package Structure

This document explains the new modular structure of WikiAccess.

## Package Organization

```
wikiaccess/
├── __init__.py           # Main package interface
├── scraper.py            # DokuWiki HTTP client
├── parser.py             # DokuWiki syntax parsing (formerly doku2word.py)  
├── converters.py         # Converter interface module
├── html_converter.py     # HTML conversion with MathJax
├── convert.py            # Word/DOCX conversion
├── equations.py          # LaTeX to OMML equation handling (formerly word_equation.py)
├── accessibility.py      # WCAG compliance checking (formerly a11y_checker.py)
├── reporting.py          # Report generation (formerly reporter.py)
├── unified.py            # High-level convenience functions
└── cli.py                # Command-line interface
```

## Usage

### As a Package
```python
from wikiaccess import convert_wiki_page, HTMLConverter, DokuWikiHTTPClient

# Simple conversion
result = convert_wiki_page(
    wiki_url="https://example.com/dokuwiki",
    page_name="my_page",
    output_dir="output"
)

# Advanced usage
client = DokuWikiHTTPClient("https://example.com/dokuwiki")
html_converter = HTMLConverter(client)
html_result = html_converter.convert_url("https://example.com/dokuwiki/doku.php?id=my_page")
```

### Command Line
```bash
# Install package
pip install .

# Use CLI
wikiaccess https://example.com/dokuwiki page1 page2 -o output/

# Or use original scripts (backward compatibility)
python convert_all.py https://example.com/dokuwiki page1 page2
```

## Installation for Development

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e .[dev]
```

## Benefits of New Structure

1. **Proper Package Structure**: Follows Python packaging best practices
2. **Clean Imports**: No namespace pollution, clear module boundaries  
3. **Entry Points**: Command-line tools installed with package
4. **Backward Compatibility**: Original scripts still work
5. **Modular Design**: Easy to import specific functionality
6. **Better Distribution**: Proper setup.py for PyPI publishing