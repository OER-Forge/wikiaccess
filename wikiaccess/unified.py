"""
WikiAccess Unified Interface

High-level convenience functions for common WikiAccess operations.
These provide simple interfaces for the most common use cases.

Uses Markdown as intermediate format:
1. DokuWiki → Markdown (simple parser)
2. Markdown → HTML/DOCX (pandoc)
3. Check accessibility
4. Generate reports
"""

from pathlib import Path
from typing import Optional, Dict, Any
from .scraper import DokuWikiHTTPClient
from .markdown_converter import MarkdownConverter
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
    Convert a single DokuWiki page to accessible documents via Markdown.
    
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
    converter = MarkdownConverter(client, output_dir)
    results = {}
    
    # Convert DokuWiki → Markdown → HTML/DOCX
    page_url = f"{wiki_url}/doku.php?id={page_name}"
    html_path, docx_path, stats = converter.convert_url(page_url)
    
    if html_path:
        results['html'] = {
            'file_path': html_path,
            'stats': stats
        }
    
    if docx_path:
        results['docx'] = {
            'file_path': docx_path,
            'stats': stats
        }
    
    # Run accessibility checks if requested
    if check_accessibility:
        checker = AccessibilityChecker()
        accessibility_results = {}
        
        if html_path:
            html_accessibility = checker.check_html(html_path)
            accessibility_results['html'] = html_accessibility
        
        if docx_path:
            docx_accessibility = checker.check_docx(docx_path)
            accessibility_results['docx'] = docx_accessibility
        
        results['accessibility'] = accessibility_results
        
        # Generate accessibility report
        if accessibility_results:
            reporter = ReportGenerator(str(output_path))
            page_display_name = page_name.replace(':', '_')
            
            html_report = accessibility_results.get('html', {})
            docx_report = accessibility_results.get('docx', {})
            
            reporter.add_page_reports(
                page_display_name,
                html_report,
                docx_report,
                results.get('html', {}).get('stats', {}),
                results.get('docx', {}).get('stats', {})
            )
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
        page_names: List of page names to convert
        output_dir: Directory to save outputs (defaults to 'output')
        formats: List of formats to generate (defaults to both)
        check_accessibility: Whether to run accessibility checks
        
    Returns:
        Dictionary mapping page names to their conversion results
    """
    if output_dir is None:
        output_dir = "output"
    
    if formats is None:
        formats = ['html', 'docx']
    
    # Collect all page results for combined report
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    client = DokuWikiHTTPClient(wiki_url)
    converter = MarkdownConverter(client, output_dir)
    
    page_results = {}
    reporter = ReportGenerator(str(output_path)) if check_accessibility else None
    
    for page_name in page_names:
        print(f"\n{'='*70}\nPage: {page_name}\n{'='*70}")
        
        try:
            page_url = f"{wiki_url}/doku.php?id={page_name}"
            html_path, docx_path, stats = converter.convert_url(page_url)
            
            results = {
                'html': {'file_path': html_path, 'stats': stats} if html_path else None,
                'docx': {'file_path': docx_path, 'stats': stats} if docx_path else None
            }
            
            # Check accessibility
            if check_accessibility:
                checker = AccessibilityChecker()
                accessibility_results = {}
                
                if html_path:
                    html_accessibility = checker.check_html(html_path)
                    accessibility_results['html'] = html_accessibility
                
                if docx_path:
                    docx_accessibility = checker.check_docx(docx_path)
                    accessibility_results['docx'] = docx_accessibility
                
                results['accessibility'] = accessibility_results
                
                # Add to reporter
                page_display_name = page_name.replace(':', '_')
                reporter.add_page_reports(
                    page_display_name,
                    accessibility_results.get('html', {}),
                    accessibility_results.get('docx', {}),
                    stats,
                    stats
                )
            
            page_results[page_name] = results
            print(f"✓ Successfully converted: {page_name}")
        
        except Exception as e:
            page_results[page_name] = {'error': str(e)}
            print(f"✗ Failed to convert {page_name}: {e}")
    
    # Generate combined reports
    if check_accessibility and reporter:
        print(f"\n{'='*70}\nGenerating Combined Accessibility Report\n{'='*70}")
        reporter.generate_detailed_reports()
        dashboard = reporter.generate_dashboard()
        print(f"\n📊 Dashboard: {dashboard}")
    
    return page_results