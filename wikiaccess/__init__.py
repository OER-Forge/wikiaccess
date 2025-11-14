"""
WikiAccess - Transform DokuWiki into Accessible Documents

A comprehensive toolkit for converting DokuWiki pages to WCAG-compliant 
HTML and Microsoft Word documents with full accessibility reporting.

Architecture (simplified via Markdown):
1. DokuWikiHTTPClient: Fetch content from DokuWiki sites
2. DokuWikiParser: Parse DokuWiki syntax → Markdown
3. MarkdownConverter: Markdown → HTML/DOCX (via Pandoc)
4. AccessibilityChecker: WCAG compliance validation
5. ReportGenerator: Generate accessibility reports

Example usage:
    from wikiaccess import convert_wiki_page
    
    convert_wiki_page(
        "https://your-wiki.com",
        "page_name"
    )
"""

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core functionality imports
from .scraper import DokuWikiHTTPClient
from .parser import DokuWikiParser, AccessibilityManager
from .markdown_converter import MarkdownConverter
from .accessibility import AccessibilityChecker
from .reporting import ReportGenerator

# Convenience imports for common use cases
from .unified import convert_wiki_page, convert_multiple_pages

__all__ = [
    # Core classes
    'DokuWikiHTTPClient',
    'DokuWikiParser', 
    'AccessibilityManager',
    'MarkdownConverter',
    'AccessibilityChecker',
    'ReportGenerator',
    
    # Convenience functions
    'convert_wiki_page',
    'convert_multiple_pages',
]