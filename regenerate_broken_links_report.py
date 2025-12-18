#!/usr/bin/env python3
"""
Regenerate comprehensive broken links report from all links in database.

This script rebuilds the broken_links_report.html with data from all conversion batches,
not just the latest batch. Shows all pages with broken links across all conversions.

Usage:
    python regenerate_broken_links_report.py              # Uses default database
    python regenerate_broken_links_report.py --db <path>  # Use specific database
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict
from wikiaccess.database import ConversionDatabase
from wikiaccess.link_rewriter import LinkRewriter


def main():
    """Regenerate broken links report from all links in database."""
    parser = argparse.ArgumentParser(
        description='Regenerate comprehensive broken links report from all batches'
    )
    parser.add_argument(
        '--db',
        default='output/conversion_history.db',
        help='Path to database'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory'
    )
    parser.add_argument(
        '--wiki-url',
        default='https://msuperl.org/wikis/pcubed',
        help='Wiki base URL'
    )

    args = parser.parse_args()

    # Connect to database
    try:
        db = ConversionDatabase(args.db)
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return 1

    try:
        # Query all broken links from database
        print(f"\n{'='*70}")
        print(f"Regenerating Comprehensive Broken Links Report")
        print(f"{'='*70}\n")

        all_broken_links = db.conn.execute('''
            SELECT DISTINCT l.source_page_id, l.target_page_id
            FROM links l
            WHERE l.resolution_status = 'missing'
            ORDER BY l.source_page_id, l.target_page_id
        ''').fetchall()

        print(f"Found {len(all_broken_links)} unique broken links in database")

        # Get all pages that have broken links (for sidebar)
        pages_with_links = db.conn.execute('''
            SELECT DISTINCT source_page_id FROM links
            WHERE resolution_status = 'missing'
            ORDER BY source_page_id
        ''').fetchall()

        page_names_list = [p[0] for p in pages_with_links]
        print(f"Found {len(page_names_list)} pages with broken links")

        # Count by target page (missing pages)
        missing_pages = defaultdict(list)
        for source, target in all_broken_links:
            missing_pages[target].append(source)

        print(f"Found {len(missing_pages)} unique missing target pages")

        # Generate the comprehensive broken links report
        if page_names_list:
            # Use the new get_all_broken_links method
            all_broken = db.get_all_broken_links()

            if all_broken:
                link_rewriter = LinkRewriter(args.wiki_url, args.output_dir, db)

                # Generate report for ALL pages with broken links
                # We'll use the regular generate_broken_links_report but pass comprehensive data
                # by temporarily setting the broken links on the rewriter

                # Build the report HTML directly
                from wikiaccess.report_components import (
                    get_breadcrumb_navigation, get_breadcrumb_javascript,
                    build_report_header, build_stat_cards
                )
                from wikiaccess.static_helper import get_css_links

                reports_dir = Path(args.output_dir) / 'reports'
                reports_dir.mkdir(parents=True, exist_ok=True)
                report_path = reports_dir / 'broken_links_report.html'

                # Build navigation
                nav_html = get_breadcrumb_navigation('broken_links', page_list=page_names_list or [], show_broken_links=True)

                # Build header
                header_html = build_report_header(
                    title="🔗 Broken Links Report",
                    subtitle="Internal wiki links pointing to pages that haven't been converted",
                    breadcrumb=[
                        {'label': '🏠 Home', 'url': 'index.html'},
                        {'label': 'Broken Links'}
                    ]
                )

                # Build stat cards
                stats_html = build_stat_cards([
                    {'value': len(all_broken), 'label': 'Broken Links', 'color': '#dc3545'},
                    {'value': sum(link['reference_count'] for link in all_broken), 'label': 'Total References', 'color': '#ff8800'}
                ], grid_size='narrow')

                # Build broken links cards
                links_html = []
                for link in all_broken:
                    target = link['target_page_id']
                    ref_count = link['reference_count']
                    referenced_by = link['referenced_by'].split(',') if link['referenced_by'] else []

                    links_html.append(f'''
            <div class="report-card bordered critical">
                <h3 class="report-card-title">Missing Page: {target}</h3>
                <p><strong>Referenced {ref_count} times  by:</strong></p>
                <div style="margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    {' '.join(f'<span class="report-badge danger">{ref}</span>' for ref in referenced_by)}
                </div>
            </div>''')

                links_section = '\n'.join(links_html)

                # Build complete HTML
                html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Broken Links Report - WikiAccess</title>
{get_css_links()}
</head>
<body>
    {nav_html}
    {get_breadcrumb_javascript()}

    <div class="report-container">
        <nav class="report-breadcrumb" aria-label="Breadcrumb"><a href="index.html" class="report-breadcrumb-item">🏠 Home</a><span class="report-breadcrumb-separator">›</span><span class="report-breadcrumb-item active">Broken Links</span></nav>
        {header_html}

        <section class="report-section">
            <h2 class="report-section-title">Summary Statistics</h2>
            <div class="report-grid narrow">
        {stats_html}
        </section>

        <section class="report-section">
            <h2 class="report-section-title">Broken Links Details</h2>
            <div class="report-grid wide">
                {links_section}
            </div>
        </section>
    </div>

    <script>
        // Navigation scripts
        {get_breadcrumb_javascript()}
    </script>
</body>
</html>'''

                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

            print(f"\n✓ Broken links report regenerated: {report_path}")
            print(f"  Unique broken links: {len(all_broken_links)}")
            print(f"  Unique missing pages: {len(missing_pages)}")
            print(f"  Pages with broken links: {len(page_names_list)}")

            # Show top missing pages
            print(f"\n  Top missing pages (by reference count):")
            sorted_missing = sorted(missing_pages.items(), key=lambda x: len(x[1]), reverse=True)
            for target, sources in sorted_missing[:10]:
                print(f"    - {target}: referenced by {len(sources)} page(s)")

            print(f"\n✓ Comprehensive broken links report regenerated successfully")
            return 0
        else:
            print(f"✗ No broken links found in database")
            return 1

    except Exception as e:
        print(f"✗ Error regenerating broken links report: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
