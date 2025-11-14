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
    
    Output structure:
        output/
        ├── markdown/
        │   └── page_name.md
        ├── images/
        │   └── [downloaded images + YouTube thumbnails]
        ├── html/
        │   └── page_name.html
        ├── docx/
        │   └── page_name.docx
        └── reports/
            ├── accessibility_report.html
            └── page_name_accessibility.html
    
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
        
        # Generate accessibility report in shared reports folder
        if accessibility_results:
            page_display_name = page_name.replace(':', '_')
            reports_dir = output_path / 'reports'
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            reporter = ReportGenerator(str(reports_dir))
            
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
    
    Output structure:
        output/
        ├── markdown/
        │   ├── page1.md
        │   └── page2.md
        ├── images/
        │   ├── page1_img.png
        │   ├── page2_img.jpg
        │   └── youtube_[id].jpg
        ├── html/
        │   ├── page1.html
        │   └── page2.html
        ├── docx/
        │   ├── page1.docx
        │   └── page2.docx
        └── reports/
            ├── accessibility_report.html (combined)
            ├── page1_accessibility.html
            └── page2_accessibility.html
    
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
    # Create separate reporter for combined report (if multiple pages)
    combined_reporter = ReportGenerator(str(output_path / 'reports')) if check_accessibility else None
    
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
                
                # Add to combined reporter
                if combined_reporter:
                    page_display_name = page_name.replace(':', '_')
                    combined_reporter.add_page_reports(
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
    
    # Generate combined report
    if check_accessibility and combined_reporter:
        print(f"\n{'='*70}\nGenerating Combined Accessibility Report\n{'='*70}")
        combined_reporter.generate_detailed_reports()
        dashboard = combined_reporter.generate_dashboard()
        print(f"\n📊 Combined Dashboard: {dashboard}")
    
    return page_results