# WikiAccess TODO List

**Last Updated**: 2025-11-24
**Project Version**: 2.0.0
**Status**: Functional for basic content; needs work for complex DokuWiki features

---

## Quick Context

WikiAccess converts DokuWiki pages to accessible HTML and DOCX documents via a Markdown intermediate format:

```
DokuWiki (HTTP scraping) → Markdown → Pandoc → HTML/DOCX + Accessibility Testing
```

**Current State**: The core pipeline works well for basic content (headings, paragraphs, lists, images, equations) but has gaps with advanced DokuWiki syntax and complex formatting.

---

## Critical Issues

### 1. Fix Corrupted convert_all.py File
**Priority**: CRITICAL
**File**: [wikiaccess/convert_all.py](wikiaccess/convert_all.py)
**Issue**: File contains corrupted/interleaved duplicate text making it non-functional
**Impact**: Backward-compatibility wrapper is broken
**Action**: Rewrite or remove this deprecated module
**Context**: This is a legacy wrapper; main functionality is in `convert_wiki_page()` which works fine

---

## High Priority

### 2. Implement DokuWiki Table Support
**Priority**: HIGH
**Status**: Marked "In Progress" in ABOUT.md but not implemented
**Files to Modify**:
- [wikiaccess/parser.py](wikiaccess/parser.py) - Add table parsing regex patterns
- [wikiaccess/markdown_converter.py](wikiaccess/markdown_converter.py) - Convert to Markdown tables

**DokuWiki Table Syntax**:
```
^ Header 1 ^ Header 2 ^ Header 3 ^
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

**Target Markdown**:
```
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

**Implementation Notes**:
- DokuWiki uses `^` for headers, `|` for cells
- Cells can span multiple columns with `|||`
- Row spans not supported in standard Markdown (may need HTML fallback)
- Table alignment indicated by spacing around cell content

**Testing**: Create test cases with simple tables, headers, alignment variations

---

### 3. Resolve latex2mathml Dependency Confusion
**Priority**: HIGH
**Issue**: `latex2mathml>=3.0.0` listed in setup.py but never imported or used
**Files Involved**:
- [setup.py](setup.py) - Lists dependency
- [requirements.txt](requirements.txt) - Lists dependency
- No actual usage in codebase

**Current Equation Handling**:
- HTML: Pandoc uses `--mathjax` flag → MathJax 3 renders in browser
- DOCX: Pandoc converts LaTeX to Word's native format (likely OMML)

**Decision Needed**:
1. **Option A**: Remove unused dependency (simplify)
2. **Option B**: Integrate latex2mathml for better MATHML support in HTML
3. **Option C**: Use latex2mathml for DOCX OMML generation

**Recommendation**: Test current Pandoc equation output quality first. If satisfactory, remove unused dependency. If equations render poorly in Word, integrate latex2mathml for OMML generation.

---

### 4. Improve DOCX Accessibility Testing
**Priority**: HIGH
**Current State**: Custom basic checks in [wikiaccess/accessibility.py](wikiaccess/accessibility.py):
- Document has title
- Language is set
- Headings exist
- Images have alt text placeholders
- Links validated

**Gap**: HTML gets comprehensive pa11y testing (80+ rules); DOCX only gets 5 basic checks

**Options**:
1. Research Python libraries for DOCX accessibility (e.g., Office Open XML validators)
2. Integrate with Microsoft Accessibility Checker API (if available)
3. Export DOCX to HTML for pa11y testing (workaround)
4. Document limitations and recommend manual DOCX accessibility review

**Action**: Research available tools/libraries for automated DOCX accessibility testing

---

## Medium Priority

### 5. Add Support for Additional DokuWiki Syntax

**Files to Modify**: [wikiaccess/parser.py](wikiaccess/parser.py)

#### 5a. Code Blocks with Syntax Highlighting
**DokuWiki Syntax**:
```
<code javascript>
function hello() {
  console.log("Hello");
}
</code>
```

**Target**: Preserve language hint for Pandoc's syntax highlighting

---

#### 5b. Monospace Text
**DokuWiki**: `%%monospace text%%`
**Target**: `` `monospace text` `` (inline code)

---

#### 5c. Superscript/Subscript
**DokuWiki**: `<sup>text</sup>`, `<sub>text</sub>`
**Markdown**: `^text^`, `~text~` (Pandoc extension)

---

#### 5d. Footnotes
**DokuWiki**: `((footnote text))`
**Markdown**: `[^1]` with `[^1]: footnote text` at bottom

---

#### 5e. Blockquotes
**DokuWiki**: Lines starting with `>`
**Markdown**: Lines starting with `>` (should already work but verify)

---

#### 5f. Description Lists
**DokuWiki**:
```
; Term
: Definition
```
**Markdown**: Use HTML `<dl>`, `<dt>`, `<dd>` tags (Pandoc supports)

---

### 6. Enhance Error Handling and Logging
**Priority**: MEDIUM
**Issues**:
- Batch processing errors are logged but user gets no feedback
- No progress indicators for long operations
- Failed image downloads silently fall back to text placeholders

**Improvements**:
1. Add progress bars for batch operations (use `tqdm` library)
2. Create detailed error log with actionable messages
3. Add retry logic with exponential backoff for media downloads
4. Implement `--verbose` flag for debugging
5. Add `--strict` mode that fails on errors vs. continuing

**Files to Modify**:
- [wikiaccess/scraper.py](wikiaccess/scraper.py) - Add retry logic
- [wikiaccess/convert_from_file_list.py](wikiaccess/convert_from_file_list.py) - Add progress indicators
- [wikiaccess/unified_interface.py](wikiaccess/unified_interface.py) - Enhanced error messages

---

### 7. Test and Document Edge Cases
**Priority**: MEDIUM
**Action Items**:
1. Create comprehensive test suite with real DokuWiki content
2. Test tables (once implemented)
3. Test complex nested lists
4. Test mixed inline formatting (bold + italic + links)
5. Test equation edge cases (inline vs display, special characters)
6. Test image URLs with special characters or authentication
7. Test YouTube video variations
8. Document known limitations in README

**Create**: `tests/fixtures/` directory with sample DokuWiki pages

---

## Low Priority

### 8. Add CSS Template System
**Priority**: LOW
**Current**: Hardcoded CSS in [wikiaccess/markdown_converter.py](wikiaccess/markdown_converter.py:337-382)
**Enhancement**: Allow users to provide custom CSS templates

**Implementation**:
1. Create `templates/` directory with default CSS
2. Add `--css-template` CLI argument
3. Support multiple themes (light, dark, high-contrast)
4. Document CSS variables for easy customization

---

### 9. Improve Media Handling
**Priority**: LOW

#### 9a. Audio/Video Beyond YouTube
- Support Vimeo, SoundCloud, etc.
- Generic video embed handling
- Audio file downloading and embedding

#### 9b. PDF Embedding
- Download PDFs referenced in wiki
- Link to PDFs in output
- Consider PDF thumbnail generation

#### 9c. SVG Handling
- Currently downloaded as static images
- Consider inline SVG for better scaling/accessibility
- Sanitize SVG for security

---

### 10. Advanced Link Resolution
**Priority**: LOW
**Current**: Handles `http(s)://` URLs and internal wiki links
**Gaps**:
- Email links: `mailto:user@example.com`
- Anchor links within same page: `#section-name`
- Inter-wiki links: `[[wp>Article]]` (Wikipedia), `[[doku>syntax]]`

**Implementation**: Expand regex patterns in [wikiaccess/parser.py](wikiaccess/parser.py)

---

### 11. Performance Optimization
**Priority**: LOW

#### 11a. Parallel Processing
- Download images in parallel (use `concurrent.futures`)
- Process multiple pages concurrently for batch operations

#### 11b. Caching
- Cache downloaded media (check if already downloaded)
- Cache authentication tokens
- Cache parsed DokuWiki content

#### 11c. Rate Limiting
- Respect server resources
- Configurable delay between requests
- Exponential backoff on errors

---

## Technical Debt

### 12. Code Quality Improvements
**Priority**: LOW

#### 12a. Type Hints
- Add type hints throughout codebase
- Run mypy for static type checking
- Files missing comprehensive type hints: most modules

#### 12b. Documentation
- Add docstrings to all public methods
- Create API documentation (Sphinx)
- Add more inline comments for complex regex patterns

#### 12c. Testing
- Current test coverage: Unknown
- Add unit tests for parser
- Add integration tests for full pipeline
- Add regression tests for known bugs

#### 12d. Refactoring
- [wikiaccess/parser.py](wikiaccess/parser.py) could be split into smaller modules
- Consider using a proper parsing library instead of regex (e.g., pyparsing)
- Extract CSS to separate file
- Create configuration object instead of passing parameters everywhere

---

## Feature Requests

### 13. Multi-Wiki Support
**Priority**: FUTURE
**Description**: Support for scraping from multiple wikis in one batch operation
**Use Case**: Organizations with federated wiki instances

---

### 14. Authentication Improvements
**Priority**: FUTURE
**Current**: Basic username/password in [wikiaccess/scraper.py](wikiaccess/scraper.py:87-127)
**Enhancements**:
- OAuth support
- API token authentication
- Session persistence
- Cookie handling improvements

---

### 15. Custom Pandoc Templates
**Priority**: FUTURE
**Description**: Allow users to provide custom Pandoc templates for DOCX/HTML generation
**Benefit**: Greater control over output formatting and styling

---

### 16. GUI Interface
**Priority**: FUTURE
**Description**: Simple GUI for non-technical users
**Options**:
- Web interface (Flask/Django)
- Desktop app (Electron, PyQt)
- Browser extension

---

## Known Limitations (Document These)

1. **Markdown Intermediate Format**: Some DokuWiki-specific formatting lost in translation
   - Colors and text backgrounds
   - Floating boxes
   - Plugin-specific syntax
   - Complex table features (row spans, cell merging)

2. **Dependency on Pandoc**: External tool must be installed separately

3. **Dependency on Node.js/pa11y**: Required for accessibility testing

4. **No Round-Trip Support**: Cannot convert back from HTML/DOCX to DokuWiki

5. **Limited Plugin Support**: DokuWiki plugins that add custom syntax not supported

6. **Network-Dependent**: All scraping requires active internet connection

---

## Project Statistics (as of 2025-11-24)

- **Total Python Code**: 3,145 lines across 9 core modules
- **Largest Modules**:
  - [wikiaccess/reporting.py](wikiaccess/reporting.py) - 668 lines
  - [wikiaccess/markdown_converter.py](wikiaccess/markdown_converter.py) - 457 lines
  - [wikiaccess/scraper.py](wikiaccess/scraper.py) - 417 lines
- **Dependencies**: 6 Python packages + Pandoc + Node.js/pa11y
- **Supported Input**: DokuWiki pages (HTTP-based)
- **Supported Output**: Markdown, HTML, DOCX + accessibility reports

---

## Quick Start for Contributors

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Pandoc
brew install pandoc  # macOS
# or: apt install pandoc  # Linux

# Install pa11y for accessibility testing
npm install

# Run a test conversion
python -c "from wikiaccess import convert_wiki_page; convert_wiki_page('https://wiki.example.com', 'namespace:page', 'output/')"
```

### Key Files to Understand
1. [wikiaccess/scraper.py](wikiaccess/scraper.py) - HTTP client and scraping logic
2. [wikiaccess/parser.py](wikiaccess/parser.py) - DokuWiki syntax parsing
3. [wikiaccess/markdown_converter.py](wikiaccess/markdown_converter.py) - Markdown generation and Pandoc orchestration
4. [wikiaccess/accessibility.py](wikiaccess/accessibility.py) - Accessibility testing
5. [wikiaccess/unified_interface.py](wikiaccess/unified_interface.py) - High-level API

### Testing Your Changes
```bash
# Test with a single page
python convert_from_file_list.py  # Uses URLS.txt

# Test markdown re-conversion (no scraping)
python convert_from_markdown.py

# Check accessibility reports in output/reports/
```

---

## Decision Log

### Why Markdown as Intermediate Format?
**Decision**: Use Markdown instead of direct DokuWiki → HTML/DOCX conversion
**Rationale**:
- Markdown is human-readable and editable
- Enables "edit and re-convert" workflow without re-scraping
- Pandoc has excellent Markdown support
- Simplifies debugging (can inspect intermediate format)
- **Trade-off**: Some DokuWiki-specific formatting lost

### Why Pandoc Instead of Custom Converters?
**Decision**: Delegate HTML/DOCX generation to Pandoc
**Rationale**:
- Battle-tested, mature tool
- Handles edge cases in document formats
- Supports equations, images, metadata automatically
- Active development and community
- **Trade-off**: External dependency, less control over output

### Why pa11y for Accessibility Testing?
**Decision**: Use pa11y (Node.js) instead of Python alternatives
**Rationale**:
- Industry standard for automated accessibility testing
- Based on axe-core (Deque Systems)
- Comprehensive WCAG 2.1 rule coverage
- Well-maintained
- **Trade-off**: Requires Node.js installation

---

## Questions for Future Investigation

1. **Should we switch from regex-based parsing to a proper parser library?**
   - Pro: More robust, handles edge cases better
   - Con: More complex, potentially slower, larger dependency

2. **Should we support exporting back to DokuWiki syntax?**
   - Use case: Round-trip editing
   - Complexity: High (Markdown → DokuWiki lossy)

3. **Should we create a plugin system for custom DokuWiki syntax?**
   - Benefit: Extensibility for site-specific needs
   - Effort: Significant architecture changes

4. **Should we support other wiki formats (MediaWiki, Confluence, etc.)?**
   - Market opportunity: Broader tool appeal
   - Scope: Would require major refactoring

5. **Is there value in creating WCAG 2.1 AA automated fixes?**
   - E.g., Auto-generate alt text with AI, fix heading hierarchy
   - Ethical concerns: Automated accessibility without human review

---

## Contact & Resources

- **Repository**: WikiAccess project (current directory)
- **Documentation**: [README.md](README.md), [ABOUT.md](ABOUT.md)
- **Dependencies**: [requirements.txt](requirements.txt), [package.json](package.json)
- **Recent Changes**: See git log (last commit: e41ba40 "updated README.md")

---

## Next Steps (Prioritized)

For someone returning to this project:

1. **First**: Fix critical file corruption in [convert_all.py](wikiaccess/convert_all.py)
2. **Then**: Implement table support (biggest feature gap)
3. **Next**: Test with real-world DokuWiki content to identify issues
4. **Finally**: Decide on equation handling (keep current vs. integrate latex2mathml)

**Quick wins**: Items 5b-5e (monospace, superscript/subscript, footnotes, blockquotes) are small parser additions that add significant value.

**Long-term vision**: Comprehensive DokuWiki accessibility conversion tool with best-in-class output quality and accessibility compliance.
