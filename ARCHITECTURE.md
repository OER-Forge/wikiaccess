# WikiAccess Architecture

## Clean Package Structure - Professional & Modular! 📦

```
wikiaccess/                           # Main package directory
├── __init__.py                       # Public API exports
├── scraper.py                        # HTTP client for DokuWiki
├── parser.py                         # DokuWiki syntax parser (was doku2word.py)
├── converters.py                     # Converter interfaces
├── html_converter.py                 # HTML generation with MathJax
├── convert.py                        # Word/DOCX generation
├── equations.py                      # LaTeX→OMML conversion (was word_equation.py)
├── accessibility.py                  # WCAG compliance checking (was a11y_checker.py)
├── reporting.py                      # Report generation (was reporter.py)
├── unified.py                        # High-level convenience functions
└── cli.py                           # Command-line interface
```

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WikiAccess Package (11 modules)              │
└─────────────────────────────────────────────────────────────────┘

Layer 0: Foundation (No Internal Dependencies)
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  scraper.py  │  │  equations.py│  │ accessibility│
│              │  │              │  │     .py      │
│ HTTP Client  │  │ LaTeX→OMML   │  │ WCAG Checker │
│ Downloads    │  │ Conversion   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

Layer 1: Core Processing (Depends on Layer 0)
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  parser.py   │  │ reporting.py │  │              │
│              │  │              │  │              │
│ DokuWiki     │  │ HTML Reports │  │              │
│ Syntax       │  │ Generation   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

Layer 2: Format Converters (Depends on Layers 0-1)  
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│html_converter│  │  convert.py  │  │converters.py │
│    .py       │  │              │  │              │
│ HTML+MathJax │  │ Word+OMML    │  │ Interfaces   │
│ Generation   │  │ Generation   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

Layer 3: User Interfaces (Depends on All Layers)
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ unified.py   │  │   cli.py     │  │ __init__.py  │
│              │  │              │  │              │
│ High-level   │  │ Command Line │  │ Public API   │
│ Functions    │  │ Interface    │  │ Exports      │
└──────────────┘  └──────────────┘  └──────────────┘
│ WCAG Checker │  │Report Builder│
└──────────────┘  └──────────────┘

                        ▼
                        
Layer 1: Converters (Use Foundation)
┌──────────────────────┐  ┌──────────────────────┐
│ html_converter.py    │  │    convert.py        │
│                      │  │                      │
│ DokuWiki → HTML      │  │ DokuWiki → DOCX      │
│ + MathJax            │  │ + OMML equations     │
│                      │  │                      │
│ Uses:                │  │ Uses:                │
│ • scraper.py         │  │ • scraper.py         │
│ • doku2word.py       │  │ • doku2word.py       │
│                      │  │ • word_equation.py   │
└──────────────────────┘  └──────────────────────┘

                        ▼

Layer 2: Applications (Use Everything)
┌────────────────────────────────────────────────┐
│        test_dual_conversion.py                 │
│                                                │
│  Example: HTML + DOCX + Reports                │
│                                                │
│  Uses ALL core modules                         │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│           convert_all.py                       │
│                                                │
│  CLI Tool: Batch conversion                    │
│                                                │
│  Uses ALL core modules                         │
└────────────────────────────────────────────────┘
```

## Data Flow

```
User Input (DokuWiki URL)
        │
        ▼
┌──────────────┐
│ scraper.py   │  Fetch page content & media
└──────┬───────┘
       │
       ▼
┌──────────────┐
│doku2word.py  │  Parse DokuWiki syntax
└──────┬───────┘
       │
       ├─────────────────┬──────────────────┐
       ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│html_converter│  │  convert.py  │  │word_equation │
│   .py        │  │              │  │    .py       │
│              │  │              │  │              │
│HTML + MathJax│  │DOCX + OMML   │  │(Used by DOCX)│
└──────┬───────┘  └──────┬───────┘  └──────────────┘
       │                 │
       │                 │
       ├─────────────────┤
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│a11y_checker  │  │              │
│   .py        │  │ HTML File    │
│              │  │ DOCX File    │
│Check WCAG    │  │              │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│ reporter.py  │  Generate accessibility reports
└──────┬───────┘
       │
       ▼
   Dashboard.html
```

## Module Responsibilities

| Module | Purpose | Dependencies | Exports |
|--------|---------|--------------|---------|
| **scraper.py** | HTTP fetching | None | `DokuWikiHTTPClient` |
| **doku2word.py** | DokuWiki parsing | None | `DokuWikiParser`, `DokuWikiToWordConverter` |
| **word_equation.py** | Equation conversion | None | `insert_mathml_equation()` |
| **a11y_checker.py** | WCAG validation | None | `AccessibilityChecker` |
| **reporter.py** | Report generation | None | `ReportGenerator` |
| **html_converter.py** | HTML output | scraper, doku2word | `HTMLConverter` |
| **convert.py** | Word output | scraper, doku2word, word_equation | `EnhancedDokuWikiConverter` |

## Why This Is Clean

✅ **No Circular Dependencies**
- Clear layered architecture
- Dependencies only flow downward

✅ **Single Responsibility**
- Each module does one thing well
- Easy to understand and maintain

✅ **Loose Coupling**
- Modules can be tested independently
- Easy to replace components

✅ **High Cohesion**
- Related functionality grouped together
- Clear module boundaries

✅ **Easy to Extend**
- Add new converters without touching core
- Add new checkers without breaking existing code

## Files NOT Needed for Core Functionality

```
test_dual_conversion.py  ← Example (useful but optional)
convert_all.py           ← CLI tool (optional)
setup.py                 ← Only for pip install
*.md files               ← Documentation
samples/                 ← Test data
output/                  ← Generated files
output_test/             ← Old test files
```

## Minimum Files for Library Use

**7 Python modules** + **requirements.txt** = 8 files total

That's it! Clean, maintainable, professional. 🎯
