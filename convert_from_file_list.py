#!/usr/bin/env python3
"""Convert URLs from URLS.txt to accessible HTML and DOCX"""

import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from wikiaccess.scraper import DokuWikiHTTPClient
from wikiaccess.converters import HTMLConverter, EnhancedDokuWikiConverter
from wikiaccess.accessibility import AccessibilityChecker
from wikiaccess.reporting import ReportGenerator

# Configuration
URL_FILE = 'URLS.txt'
OUTPUT_DIR = 'output'

def parse_dokuwiki_url(url):
    """Extract base URL and page ID from a DokuWiki URL"""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/doku.php', 1)[0]}"
    page_id = parse_qs(parsed.query).get('id', [''])[0]
    return base_url, page_id

def main():
    # Read URLs
    url_file = Path(URL_FILE)
    if not url_file.exists():
        print(f"Error: {URL_FILE} not found")
        sys.exit(1)
    
    urls = [line.strip().strip('\'"') for line in url_file.read_text().splitlines() 
            if line.strip() and not line.startswith('#')]
    
    if not urls:
        print(f"Error: No URLs found in {URL_FILE}")
        sys.exit(1)
    
    print(f"Converting {len(urls)} URLs from {URL_FILE}...")
    
    # Setup
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    checker = AccessibilityChecker()
    reporter = ReportGenerator(OUTPUT_DIR)
    
    # Convert each URL
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        try:
            base_url, page_id = parse_dokuwiki_url(url)
            page_name = page_id.replace(':', '_')
            
            # Initialize client and converters
            client = DokuWikiHTTPClient(base_url)
            html_converter = HTMLConverter(client)
            docx_converter = EnhancedDokuWikiConverter(client)
            
            # Convert to HTML
            page_url = f"{base_url}/doku.php?id={page_id}"
            html_path, html_stats = html_converter.convert_url(page_url)
            
            # Convert to DOCX
            docx_path = output_path / f"{page_name}.docx"
            docx_stats = docx_converter.convert_url(page_url, str(docx_path))
            
            # Check accessibility
            html_report = checker.check_html(html_path)
            docx_report = checker.check_docx(str(docx_path))
            
            # Add to reporter
            reporter.add_page_reports(page_name, html_report, docx_report, html_stats, docx_stats)
            
            print("✓ Done")
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    # Generate final report
    print("\n📊 Generating accessibility report...")
    reporter.generate_detailed_reports()
    dashboard = reporter.generate_dashboard()
    print(f"✓ Report: {dashboard}")
    print(f"\n✓ All conversions complete. Output in {OUTPUT_DIR}/")

if __name__ == '__main__':
    main()

