#!/usr/bin/env python3
"""Convert URLs from URLS.txt to accessible HTML, DOCX, and Markdown"""

import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from wikiaccess.unified import convert_multiple_pages

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
    
    print(f"Converting {len(urls)} URLs from {URL_FILE}...\n")
    
    # Extract page IDs from URLs
    page_ids = []
    wiki_url = None
    
    for url in urls:
        base_url, page_id = parse_dokuwiki_url(url)
        if wiki_url is None:
            wiki_url = base_url
        page_ids.append(page_id)
    
    if not wiki_url:
        print(f"Error: Could not parse wiki URL")
        sys.exit(1)
    
    # Use unified interface to convert multiple pages
    # This generates Markdown + HTML + DOCX + Accessibility reports
    results = convert_multiple_pages(
        wiki_url=wiki_url,
        page_names=page_ids,
        output_dir=OUTPUT_DIR,
        formats=['html', 'docx'],
        check_accessibility=True
    )
    
    # Summary
    print(f"\n{'='*70}")
    print("CONVERSION SUMMARY")
    print(f"{'='*70}")
    
    success_count = sum(1 for r in results.values() if 'error' not in r)
    error_count = len(results) - success_count
    
    print(f"✓ Successful: {success_count}/{len(results)}")
    if error_count > 0:
        print(f"✗ Failed: {error_count}/{len(results)}")
    
    print(f"\nOutput directory: {OUTPUT_DIR}/")
    print(f"  - Markdown files: {OUTPUT_DIR}/*.md")
    print(f"  - HTML files: {OUTPUT_DIR}/html/")
    print(f"  - DOCX files: {OUTPUT_DIR}/docx/")
    print(f"  - Images: {OUTPUT_DIR}/images/")
    print(f"  - Accessibility report: {OUTPUT_DIR}/accessibility_report.html")

if __name__ == '__main__':
    main()

