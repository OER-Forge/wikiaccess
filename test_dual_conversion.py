#!/usr/bin/env python3
"""
WikiAccess - Test Dual-Format Conversion

Demonstrates converting a DokuWiki page to both accessible HTML and Word formats,
then generating comprehensive WCAG compliance reports.

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

from wikiaccess.scraper import DokuWikiHTTPClient
from wikiaccess.converters import HTMLConverter, EnhancedDokuWikiConverter
from wikiaccess.accessibility import AccessibilityChecker
from wikiaccess.reporting import ReportGenerator
from pathlib import Path

# Setup
wiki_url = 'https://msuperl.org/wikis/pcubed'
page_url = 'https://msuperl.org/wikis/pcubed/doku.php?id=183_notes:scalars_and_vectors'
output_dir = Path('output')

# Create directories
html_dir = output_dir / 'html'
docx_dir = output_dir / 'docx'
html_dir.mkdir(parents=True, exist_ok=True)
docx_dir.mkdir(parents=True, exist_ok=True)

# Initialize
client = DokuWikiHTTPClient(wiki_url)
html_converter = HTMLConverter(client)
docx_converter = EnhancedDokuWikiConverter(client)
checker = AccessibilityChecker()
reporter = ReportGenerator(str(output_dir))

print("\n" + "="*70)
print("DUAL FORMAT CONVERSION WITH ACCESSIBILITY CHECKING")
print("="*70)

# Get page
result = client.get_page_from_url(page_url)
if not result:
    print("✗ Failed to fetch page")
    exit(1)

page_id, content = result
page_name = page_id.replace(':', '_')

print(f"\n✓ Fetched page: {page_id}")

# Convert to HTML
html_path = html_dir / f'{page_name}.html'
print(f"\n📄 Converting to HTML...")
_, html_stats = html_converter.convert_url(page_url, str(html_path))

# Convert to DOCX
docx_path = docx_dir / f'{page_name}.docx'
print(f"\n📄 Converting to DOCX...")
docx_stats = docx_converter.convert_url(page_url, str(docx_path))

# Check accessibility
print(f"\n🔍 Checking HTML accessibility...")
html_report = checker.check_html(str(html_path))

print(f"\n🔍 Checking DOCX accessibility...")
docx_report = checker.check_docx(str(docx_path))

# Add to reporter
reporter.add_page_reports(page_name, html_report, docx_report, html_stats, docx_stats)

# Generate reports
print(f"\n📊 Generating accessibility reports...")
reporter.generate_detailed_reports()
dashboard = reporter.generate_dashboard()

print("\n" + "="*70)
print("✓ CONVERSION COMPLETE")
print("="*70)
print(f"\nHTML output: {html_path}")
print(f"DOCX output: {docx_path}")
print(f"Dashboard: {dashboard}")
print(f"\nHTML WCAG AA: {html_report['score_aa']}%")
print(f"HTML WCAG AAA: {html_report['score_aaa']}%")
print(f"DOCX WCAG AA: {docx_report['score_aa']}%")
print(f"DOCX WCAG AAA: {docx_report['score_aaa']}%")
print("\n")
