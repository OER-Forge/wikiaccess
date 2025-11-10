"""
WikiAccess - Transform DokuWiki into Accessible Documents

A comprehensive toolkit for converting DokuWiki pages to WCAG-compliant 
HTML and Microsoft Word documents with full accessibility reporting.

Main Components:
- DokuWikiHTTPClient: Fetch content from DokuWiki sites
- HTMLConverter: Convert to accessible HTML with MathJax
- EnhancedDokuWikiConverter: Convert to Word with OMML equations
- AccessibilityChecker: WCAG compliance validation
- ReportGenerator: Generate accessibility reports

Example usage:
    from wikiaccess import DokuWikiHTTPClient, HTMLConverter
    
    client = DokuWikiHTTPClient("https://your-wiki.com")
    converter = HTMLConverter()
    result = converter.convert_page_to_html(client, "page_name")
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core functionality imports
from .scraper import DokuWikiHTTPClient
from .parser import DokuWikiParser, AccessibilityManager
from .converters import (
    HTMLConverter,
    EnhancedDokuWikiConverter,
    DokuWikiToWordConverter
)
from .accessibility import AccessibilityChecker
from .reporting import ReportGenerator
from .equations import insert_mathml_equation

# Convenience imports for common use cases
from .unified import convert_wiki_page, convert_multiple_pages

__all__ = [
    # Core classes
    'DokuWikiHTTPClient',
    'DokuWikiParser', 
    'AccessibilityManager',
    'HTMLConverter',
    'EnhancedDokuWikiConverter', 
    'DokuWikiToWordConverter',
    'AccessibilityChecker',
    'ReportGenerator',
    
    # Utility functions
    'insert_mathml_equation',
    'convert_wiki_page',
    'convert_multiple_pages',
]