"""
WikiAccess Unified Interface

High-level convenience functions for common WikiAccess operations.
These provide simple interfaces for the most common use cases.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from .scraper import DokuWikiHTTPClient
from .converters import HTMLConverter, EnhancedDokuWikiConverter
from .accessibility import AccessibilityChecker
from .reporting import ReportGenerator


def convert_wiki_page(
    wiki_url: str,
    page_name: str,
    output_dir: Optional[str] = None,
    formats: Optional[list] = None,
    check_accessibility: bool = True
) -> Dict[str, Any]:
    """
    Convert a single DokuWiki page to accessible documents.
    
    Args:
        wiki_url: Base URL of the DokuWiki site
        page_name: Name of the wiki page to convert
        output_dir: Directory to save outputs (defaults to 'output')
        formats: List of formats to generate ['html', 'docx'] (defaults to both)
        check_accessibility: Whether to run accessibility checks
        
    Returns:
        Dictionary with paths to generated files and accessibility results
    """
    if output_dir is None:
        output_dir = "output"
    
    if formats is None:
        formats = ['html', 'docx']
        
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize components
    client = DokuWikiHTTPClient(wiki_url)
    results = {}
    
    # Generate HTML if requested
    if 'html' in formats:
        html_converter = HTMLConverter(client)
        page_url = f"{wiki_url}/doku.php?id={page_name}"
        html_output_path, html_stats = html_converter.convert_url(page_url)
        results['html'] = {
            'file_path': html_output_path,
            'stats': html_stats
        }
    
    # Generate DOCX if requested  
    if 'docx' in formats:
        word_converter = EnhancedDokuWikiConverter(client)
        page_url = f"{wiki_url}/doku.php?id={page_name}"
        docx_output_path = output_path / f"{page_name.replace(':', '_')}.docx"
        docx_stats = word_converter.convert_url(page_url, str(docx_output_path))
        results['docx'] = {
            'file_path': str(docx_output_path),
            'stats': docx_stats
        }
        
        # Run accessibility checks if requested
    if check_accessibility:
        checker = AccessibilityChecker()
        accessibility_results = {}
        
        if 'html' in results:
            html_accessibility = checker.check_html(results['html']['file_path'])
            accessibility_results['html'] = html_accessibility
            
        if 'docx' in results:
            docx_accessibility = checker.check_docx(results['docx']['file_path'])
            accessibility_results['docx'] = docx_accessibility
            
        results['accessibility'] = accessibility_results
        
        # Generate accessibility report
        if accessibility_results:
            reporter = ReportGenerator(str(output_path))
            # Add the reports to the reporter
            page_display_name = page_name.replace(':', '_')
            reporter.add_page_reports(
                page_display_name,
                accessibility_results.get('html', {}),
                accessibility_results.get('docx', {}),
                results.get('html', {}).get('stats', {}),
                results.get('docx', {}).get('stats', {})
            )
            # Generate the detailed reports and dashboard
            reporter.generate_detailed_reports()
            dashboard_path = reporter.generate_dashboard()
            results['accessibility_report'] = dashboard_path
    
    return results


def convert_multiple_pages(
    wiki_url: str, 
    page_names: list,
    output_dir: Optional[str] = None,
    formats: Optional[list] = None,
    check_accessibility: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Convert multiple DokuWiki pages to accessible documents.
    
    Args:
        wiki_url: Base URL of the DokuWiki site
        page_names: List of wiki page names to convert
        output_dir: Directory to save outputs (defaults to 'output')
        formats: List of formats to generate ['html', 'docx'] (defaults to both)
        check_accessibility: Whether to run accessibility checks
        
    Returns:
        Dictionary mapping page names to their conversion results
    """
    results = {}
    
    for page_name in page_names:
        try:
            page_result = convert_wiki_page(
                wiki_url=wiki_url,
                page_name=page_name,
                output_dir=output_dir,
                formats=formats,
                check_accessibility=check_accessibility
            )
            results[page_name] = page_result
        except Exception as e:
            results[page_name] = {'error': str(e)}
            
    return results