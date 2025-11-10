# About WikiAccess

**Transform DokuWiki into Accessible Documents**

## What is WikiAccess?

WikiAccess is a comprehensive Python package for converting DokuWiki content into accessible HTML and Microsoft Word documents with full WCAG 2.1 AA/AAA compliance checking. It's designed for educational institutions, documentation teams, and organizations that need to ensure their content meets accessibility standards.

## Key Features

✨ **Dual-Format Output**: Generate both HTML (with MathJax) and Word documents (with native OMML equations)  
♿ **WCAG Compliance**: Comprehensive accessibility checking and reporting  
🌐 **No API Required**: Works with any DokuWiki instance via HTTP  
📐 **Advanced Equations**: LaTeX → MathJax (HTML) & OMML (Word) conversion  
🖼️ **Rich Media**: Automatic image downloading and YouTube video embedding  
📊 **Detailed Reports**: Visual accessibility dashboards and compliance scoring

## The Problem

Educational institutions and organizations use DokuWiki for collaborative content creation, but often struggle to:
- Export content to accessible formats for compliance
- Ensure WCAG 2.1 AA/AAA standards are met  
- Properly convert mathematical equations
- Embed media while maintaining accessibility
- Generate audit reports for accessibility compliance
- Provide content in multiple accessible formats

## The Solution

WikiAccess provides:
- **One-click conversion** from DokuWiki to accessible HTML + Word
- **Automatic accessibility checking** with detailed WCAG compliance reports  
- **Professional equation handling** (LaTeX → MathJax + OMML)
- **Smart media embedding** with proper alt-text and accessibility metadata
- **Comprehensive reporting** for accessibility audits and compliance documentation
1. **Dual-Format Output**: Generate both accessible HTML (MathJax) and Word (OMML equations)
2. **Accessibility Reports**: Comprehensive WCAG AA/AAA compliance dashboards
3. **Media Tracking**: Monitor image/video embedding success rates
4. **Native Equations**: LaTeX → MathJax (HTML) & OMML (Word) - fully editable
5. **No API Required**: Fetches content via HTTP from any DokuWiki instance

## Key Features

### 📄 Dual-Format Conversion
- **HTML Output**: Semantic HTML5, MathJax 3, high contrast + dark mode
- **Word Output**: Native OMML equations, embedded media, full accessibility metadata

### ♿ Accessibility First
- WCAG 2.1 Level AA compliance (primary target)
- WCAG 2.1 Level AAA compliance (stretch goal)
- Automated compliance checking
- Detailed issue reporting with recommendations

### 📊 Comprehensive Reporting
- Side-by-side HTML vs Word comparison
- Media conversion statistics (images/videos/equations)
- Issue detection (headings, contrast, alt-text)
- Clickable links to converted files

### 📐 Advanced Equation Support
- **HTML**: MathJax 3 with accessibility features
- **Word**: Native OMML objects (click to edit in Word)
- Inline and display equations
- Complex LaTeX: fractions, vectors, Greek letters, superscripts, subscripts

## Who Is It For?

- **Educators**: Creating accessible course materials
- **Technical Writers**: Converting documentation to distributable formats
- **Accessibility Officers**: Ensuring compliance and generating reports
- **Content Managers**: Archiving wiki content with full media

## Technology Stack

Built with:
- **Python 3.7+**: Core language
- **python-docx**: Word document generation
- **MathJax 3**: Accessible math rendering for HTML
- **latex2mathml**: LaTeX equation parsing
- **BeautifulSoup**: HTML parsing and analysis
- **Pillow**: Image processing

## Philosophy

WikiAccess is built on these principles:

1. **Accessibility First**: WCAG compliance is not optional
2. **Transparency**: Detailed reports show exactly what's working
3. **No Compromises**: Both formats get full feature support
4. **Standards-Based**: Native formats (OMML, MathJax) over workarounds
5. **User-Friendly**: Clear reports, helpful error messages

## Project Status

**Current Version**: 1.0.0

✅ **Completed**:
- Dual HTML/DOCX output
- WCAG AA/AAA compliance checking
- Media embedding with success tracking
- LaTeX → MathJax/OMML conversion
- Accessibility reporting dashboard
- HTTP fetching (no API required)

🚧 **In Progress**:
- Table support
- Additional LaTeX features
- Custom styling templates

💡 **Planned**:
- Batch conversion tools
- CLI tool with progress bars
- Plugin system for custom syntax
- Performance optimizations

## Contributing

We welcome contributions! See the main README for areas where help is needed.

## License

MIT License - Free for educational and commercial use

---

**WikiAccess** - Making documentation accessible to everyone

*"Access to information is a fundamental right. Let's make it truly accessible."*
