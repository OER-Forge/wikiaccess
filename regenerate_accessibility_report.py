#!/usr/bin/env python3
"""
Regenerate comprehensive accessibility report from database.

This script rebuilds the accessibility_report.html with ALL pages from the database,
ensuring the report is always comprehensive and up-to-date across all batches.

Usage:
    python regenerate_accessibility_report.py
    python regenerate_accessibility_report.py --db output/conversion_history.db
"""

import argparse
import sys
from pathlib import Path

from wikiaccess.database import ConversionDatabase
from wikiaccess.reporting import ReportGenerator
from wikiaccess.hub_reporting import HubReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Regenerate comprehensive accessibility report from database'
    )
    parser.add_argument(
        '--db',
        default='output/conversion_history.db',
        help='Path to database'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for reports'
    )

    args = parser.parse_args()

    # Connect to database
    try:
        db = ConversionDatabase(args.db)
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return 1

    # Query all pages from database
    try:
        all_pages = db.conn.execute('''
            SELECT p.page_id, p.html_wcag_aa_score, p.html_wcag_aaa_score,
                   p.docx_wcag_aa_score, p.docx_wcag_aaa_score
            FROM pages p
            ORDER BY p.page_id
        ''').fetchall()
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        db.close()
        return 1

    if not all_pages:
        print("✓ No pages in database to report on")
        db.close()
        return 0

    print(f"\n{'='*70}")
    print(f"Regenerating Comprehensive Accessibility Report")
    print(f"{'='*70}\n")
    print(f"Found {len(all_pages)} pages in database\n")

    try:
        # Create reporter
        reports_dir = Path(args.output_dir) / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        comprehensive_reporter = ReportGenerator(str(reports_dir))

        # Add all pages
        for i, page_row in enumerate(all_pages, 1):
            page_id = page_row[0]
            page_display_name = page_id.replace(':', '_')

            # Build report structure from database
            html_report = {
                'score_aa': page_row[1] or 0,
                'score_aaa': page_row[2] or 0,
                'issues_aa': [],
                'issues_aaa': [],
                'warnings': []
            }
            docx_report = {
                'score_aa': page_row[3] or 0,
                'score_aaa': page_row[4] or 0,
                'issues_aa': [],
                'issues_aaa': [],
                'warnings': []
            }
            comprehensive_reporter.add_page_reports(
                page_display_name,
                html_report,
                docx_report
            )

            if i % 20 == 0 or i == len(all_pages):
                print(f"  Added {i}/{len(all_pages)} pages...")

        # Generate the reports
        print(f"\nGenerating detailed reports...")
        comprehensive_reporter.generate_detailed_reports()

        print(f"Generating comprehensive dashboard...")
        dashboard_path = comprehensive_reporter.generate_dashboard()

        print(f"\n{'='*70}")
        print(f"✓ Successfully regenerated accessibility report!")
        print(f"{'='*70}")
        print(f"  Pages: {len(all_pages)}")
        print(f"  Report: {dashboard_path}\n")

        # Also regenerate landing hub (index.html) with all pages
        print(f"Regenerating landing hub (index.html)...")
        try:
            hub_generator = HubReportGenerator(str(reports_dir))

            # Build page_reports dict for hub generator
            page_reports = {}
            for page_row in all_pages:
                page_id = page_row[0]
                page_display_name = page_id.replace(':', '_')
                page_reports[page_display_name] = {
                    'html': {
                        'score_aa': page_row[1] or 0,
                        'score_aaa': page_row[2] or 0,
                    },
                    'docx': {
                        'score_aa': page_row[3] or 0,
                        'score_aaa': page_row[4] or 0,
                    }
                }

            # Generate the hub
            hub_path = hub_generator.generate_hub(page_reports, [])
            print(f"✓ Landing hub updated: {hub_path}\n")

        except Exception as e:
            print(f"⚠️  Warning: Could not regenerate landing hub: {e}\n")

        return 0

    except Exception as e:
        print(f"✗ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
