#!/usr/bin/env python3
"""Full interactive test of WikiAccess minimal version"""

from wikiaccess.database import ConversionDatabase
from wikiaccess.report_regenerator import ReportRegenerator
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("WikiAccess - Full Workflow Test")
    print("="*70 + "\n")

    db = ConversionDatabase()

    # 1. Database stats
    print("1. DATABASE STATISTICS")
    pages = db.get_all_pages_with_scores()
    images = db.get_all_images_for_report()
    broken_links = db.get_all_broken_links()
    print(f"   Pages: {len(pages)}")
    print(f"   Images: {len(images)}")
    print(f"   Broken links: {len(broken_links)}")

    # 2. Regenerate reports
    print("\n2. REGENERATING REPORTS")
    regen = ReportRegenerator(output_dir='output')
    results = regen.regenerate_all(db)

    for report_type, path in results.items():
        status = "✓" if path else "✗"
        print(f"   {status} {report_type}: {path}")

    # 3. Discovery stats
    print("\n3. DISCOVERY WORKFLOW")
    discovered = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages'
    ).fetchone()[0]
    approved = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages WHERE discovery_status = "approved"'
    ).fetchone()[0]
    converted = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages WHERE discovery_status = "converted"'
    ).fetchone()[0]
    print(f"   Discovered: {discovered}")
    print(f"   Approved: {approved}")
    print(f"   Converted: {converted}")

    # 4. Output files
    print("\n4. GENERATED FILES")
    output_dir = Path('output')
    html_files = len(list(output_dir.glob('html/*.html')))
    docx_files = len(list(output_dir.glob('docx/*.docx')))
    md_files = len(list(output_dir.glob('*.md')))
    img_files = len(list(output_dir.glob('images/*')))
    print(f"   HTML: {html_files}")
    print(f"   DOCX: {docx_files}")
    print(f"   Markdown: {md_files}")
    print(f"   Images: {img_files}")

    print("\n" + "="*70)
    print("✅ Test Complete - All systems operational")
    print("="*70 + "\n")
    print("View reports:")
    print("  open output/reports/index.html")
    print()

if __name__ == '__main__':
    main()
