#!/usr/bin/env python3
"""
Convert existing Markdown files to HTML and DOCX without scraping.

Usage:
    python convert_from_markdown.py                    # Convert all .md files in output/markdown/
    python convert_from_markdown.py file1.md file2.md  # Convert specific files
"""

import sys
from pathlib import Path
from wikiaccess.scraper import DokuWikiHTTPClient
from wikiaccess.markdown_converter import MarkdownConverter
from wikiaccess.accessibility import AccessibilityChecker
from wikiaccess.reporting import ReportGenerator


def convert_markdown_files(markdown_files=None, output_dir='output'):
    """Convert markdown files to HTML and DOCX"""
    
    output_path = Path(output_dir)
    markdown_dir = output_path / 'markdown'
    
    # If no files specified, convert all markdown files
    if not markdown_files:
        markdown_files = list(markdown_dir.glob('*.md'))
    else:
        # Convert relative paths to full paths
        markdown_files = [
            Path(f) if Path(f).is_absolute() else Path(f)
            for f in markdown_files
        ]
    
    if not markdown_files:
        print(f"No markdown files found in {markdown_dir}")
        return
    
    print(f"\nConverting {len(markdown_files)} markdown files...\n")
    
    # Initialize converter (need dummy client)
    client = DokuWikiHTTPClient("http://localhost")
    converter = MarkdownConverter(client, output_dir)
    
    reporter = ReportGenerator(str(output_path / 'reports'))
    results = {}
    
    for md_file in markdown_files:
        md_file = Path(md_file)
        if not md_file.exists():
            print(f"✗ File not found: {md_file}")
            continue
        
        page_name = md_file.stem
        print(f"Converting: {page_name}")
        
        try:
            # Convert markdown to HTML
            html_path = converter.html_dir / f"{page_name}.html"
            converter._pandoc_convert(str(md_file), str(html_path), 'html')
            
            # Convert markdown to DOCX
            docx_path = converter.docx_dir / f"{page_name}.docx"
            converter._pandoc_convert(str(md_file), str(docx_path), 'docx')
            
            # Check accessibility
            checker = AccessibilityChecker()
            html_accessibility = checker.check_html(str(html_path))
            docx_accessibility = checker.check_docx(str(docx_path))
            
            # Add to reporter
            reporter.add_page_reports(
                page_name,
                html_accessibility,
                docx_accessibility,
                {},
                {}
            )
            
            results[page_name] = {
                'html': str(html_path),
                'docx': str(docx_path)
            }
            
            print(f"✓ {page_name}")
        
        except Exception as e:
            print(f"✗ {page_name}: {e}")
            results[page_name] = {'error': str(e)}
    
    # Generate reports
    print("\nGenerating accessibility report...")
    reporter.generate_detailed_reports()
    dashboard = reporter.generate_dashboard()
    
    print(f"\n✓ Complete! Report: {dashboard}")
    print(f"HTML files: {converter.html_dir}/")
    print(f"DOCX files: {converter.docx_dir}/")
    
    return results


if __name__ == '__main__':
    # Get markdown files from command line or use all
    markdown_files = sys.argv[1:] if len(sys.argv) > 1 else None
    convert_markdown_files(markdown_files)
