#!/usr/bin/env python3
"""
Database Query Utility for WikiAccess

Provides convenient CLI commands for querying conversion history,
analyzing trends, and managing the conversion database.

Usage:
    python db_query.py list-batches
    python db_query.py batch-info <batch_id>
    python db_query.py page-history <wiki_url> <page_id>
    python db_query.py failed-pages <batch_id>
    python db_query.py broken-images
    python db_query.py accessibility-trends <wiki_url> <page_id>
    python db_query.py export-csv <batch_id> <output_file>
"""

import sys
import csv
from pathlib import Path
from wikiaccess.database import ConversionDatabase


def list_batches(db: ConversionDatabase):
    """List all conversion batches."""
    cursor = db.conn.execute("""
        SELECT batch_id, wiki_url, started_at, completed_at,
               total_pages, successful_pages, failed_pages
        FROM conversion_batches
        ORDER BY started_at DESC
    """)

    print(f"\n{'='*100}")
    print(f"{'Batch ID':<30} {'Wiki URL':<30} {'Started':<20} {'Pages':<10} {'Success':<8}")
    print(f"{'='*100}")

    for row in cursor.fetchall():
        batch_id = row['batch_id']
        wiki_url = row['wiki_url'][:27] + '...' if len(row['wiki_url']) > 30 else row['wiki_url']
        started = row['started_at'][:19] if row['started_at'] else 'N/A'
        total = row['total_pages'] or 0
        success = row['successful_pages'] or 0

        print(f"{batch_id:<30} {wiki_url:<30} {started:<20} {total:<10} {success:<8}")

    print(f"{'='*100}\n")


def batch_info(db: ConversionDatabase, batch_id: str):
    """Show detailed information about a batch."""
    info = db.get_batch_info(batch_id)

    if not info:
        print(f"❌ Batch not found: {batch_id}")
        return

    print(f"\n{'='*70}")
    print(f"Batch Information: {batch_id}")
    print(f"{'='*70}")
    print(f"Wiki URL: {info['wiki_url']}")
    print(f"Started: {info['started_at']}")
    print(f"Completed: {info['completed_at'] or 'In Progress'}")
    print(f"\nStatistics:")
    print(f"  Total Pages: {info['total_pages']}")
    print(f"  Successful: {info['successful_pages']}")
    print(f"  Failed: {info['failed_pages']}")
    print(f"  Total Images: {info['total_images']}")
    print(f"  Failed Images: {info['failed_images']}")
    print(f"{'='*70}\n")

    # Show failed pages if any
    failed = db.get_failed_pages(batch_id)
    if failed:
        print(f"\n❌ Failed Pages ({len(failed)}):")
        for page_id in failed:
            print(f"  - {page_id}")

    # Show successful pages
    success = db.get_converted_pages(batch_id)
    if success:
        print(f"\n✓ Successful Pages ({len(success)}):")
        for page_id in success[:10]:  # Show first 10
            print(f"  - {page_id}")
        if len(success) > 10:
            print(f"  ... and {len(success) - 10} more")


def page_history(db: ConversionDatabase, wiki_url: str, page_id: str):
    """Show conversion history for a specific page."""
    history = db.get_page_history(wiki_url, page_id, limit=10)

    if not history:
        print(f"❌ No history found for: {page_id}")
        return

    print(f"\n{'='*100}")
    print(f"Conversion History: {page_id}")
    print(f"{'='*100}")
    print(f"{'Date':<20} {'Status':<10} {'HTML Score':<12} {'DOCX Score':<12} {'Images':<10} {'Duration':<10}")
    print(f"{'='*100}")

    for record in history:
        date = record['converted_at'][:19] if record['converted_at'] else 'N/A'
        status = record['conversion_status']
        html_score = f"{record['html_wcag_aa_score']}%" if record['html_wcag_aa_score'] else 'N/A'
        docx_score = f"{record['docx_wcag_aa_score']}%" if record['docx_wcag_aa_score'] else 'N/A'
        images = f"{record['image_success_count']}/{record['image_count']}"
        duration = f"{record['conversion_duration_seconds']:.1f}s" if record['conversion_duration_seconds'] else 'N/A'

        print(f"{date:<20} {status:<10} {html_score:<12} {docx_score:<12} {images:<10} {duration:<10}")

    print(f"{'='*100}\n")

    # Show accessibility trends
    trends = db.get_accessibility_trends(wiki_url, page_id)
    if len(trends) > 1:
        print("\n📊 Accessibility Trend:")
        first = trends[0]
        last = trends[-1]

        if first['html_wcag_aa_score'] and last['html_wcag_aa_score']:
            diff = last['html_wcag_aa_score'] - first['html_wcag_aa_score']
            arrow = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
            print(f"  HTML WCAG AA: {first['html_wcag_aa_score']}% → {last['html_wcag_aa_score']}% {arrow} ({diff:+d}%)")


def failed_pages(db: ConversionDatabase, batch_id: str):
    """List all failed pages in a batch."""
    failed = db.get_failed_pages(batch_id)

    if not failed:
        print(f"✓ No failed pages in batch: {batch_id}")
        return

    print(f"\n{'='*70}")
    print(f"Failed Pages in Batch: {batch_id}")
    print(f"{'='*70}")

    # Get details for each failed page
    for page_id in failed:
        cursor = db.conn.execute("""
            SELECT error_message FROM pages
            WHERE batch_id = ? AND page_id = ? AND conversion_status = 'FAILED'
            ORDER BY converted_at DESC LIMIT 1
        """, (batch_id, page_id))

        row = cursor.fetchone()
        error = row['error_message'] if row and row['error_message'] else 'Unknown error'

        print(f"\n❌ {page_id}")
        print(f"   Error: {error}")

    print(f"\n{'='*70}\n")


def broken_images(db: ConversionDatabase):
    """Show statistics on broken/failed images."""
    stats = db.get_image_failure_stats()

    if not stats:
        print("✓ No failed images found")
        return

    print(f"\n{'='*100}")
    print(f"Image Failure Statistics")
    print(f"{'='*100}")
    print(f"{'Source URL':<60} {'Failed':<10} {'Total':<10} {'Rate':<10}")
    print(f"{'='*100}")

    for stat in stats[:20]:  # Show top 20
        url = stat['source_url'][:57] + '...' if len(stat['source_url']) > 60 else stat['source_url']
        failed = stat['failure_count']
        total = stat['total_attempts']
        rate = f"{stat['failure_rate']:.1f}%"

        print(f"{url:<60} {failed:<10} {total:<10} {rate:<10}")

    print(f"{'='*100}\n")


def accessibility_trends(db: ConversionDatabase, wiki_url: str, page_id: str):
    """Show accessibility score trends over time."""
    trends = db.get_accessibility_trends(wiki_url, page_id)

    if not trends:
        print(f"❌ No accessibility data found for: {page_id}")
        return

    print(f"\n{'='*80}")
    print(f"Accessibility Trends: {page_id}")
    print(f"{'='*80}")
    print(f"{'Date':<20} {'HTML AA':<10} {'HTML AAA':<10} {'DOCX AA':<10} {'DOCX AAA':<10}")
    print(f"{'='*80}")

    for record in trends:
        date = record['converted_at'][:19] if record['converted_at'] else 'N/A'
        html_aa = f"{record['html_wcag_aa_score']}%" if record['html_wcag_aa_score'] else 'N/A'
        html_aaa = f"{record['html_wcag_aaa_score']}%" if record['html_wcag_aaa_score'] else 'N/A'
        docx_aa = f"{record['docx_wcag_aa_score']}%" if record['docx_wcag_aa_score'] else 'N/A'
        docx_aaa = f"{record['docx_wcag_aaa_score']}%" if record['docx_wcag_aaa_score'] else 'N/A'

        print(f"{date:<20} {html_aa:<10} {html_aaa:<10} {docx_aa:<10} {docx_aaa:<10}")

    print(f"{'='*80}\n")


def export_csv(db: ConversionDatabase, batch_id: str, output_file: str):
    """Export batch data to CSV."""
    cursor = db.conn.execute("""
        SELECT
            page_id,
            conversion_status,
            html_path,
            docx_path,
            html_wcag_aa_score,
            html_wcag_aaa_score,
            docx_wcag_aa_score,
            docx_wcag_aaa_score,
            image_count,
            image_success_count,
            image_failed_count,
            converted_at,
            conversion_duration_seconds,
            error_message
        FROM pages
        WHERE batch_id = ?
        ORDER BY page_id
    """, (batch_id,))

    rows = cursor.fetchall()

    if not rows:
        print(f"❌ No pages found for batch: {batch_id}")
        return

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            'Page ID', 'Status', 'HTML Path', 'DOCX Path',
            'HTML WCAG AA', 'HTML WCAG AAA', 'DOCX WCAG AA', 'DOCX WCAG AAA',
            'Total Images', 'Success Images', 'Failed Images',
            'Converted At', 'Duration (s)', 'Error'
        ])

        # Write data
        for row in rows:
            writer.writerow([
                row['page_id'],
                row['conversion_status'],
                row['html_path'] or '',
                row['docx_path'] or '',
                row['html_wcag_aa_score'] or '',
                row['html_wcag_aaa_score'] or '',
                row['docx_wcag_aa_score'] or '',
                row['docx_wcag_aaa_score'] or '',
                row['image_count'],
                row['image_success_count'],
                row['image_failed_count'],
                row['converted_at'] or '',
                f"{row['conversion_duration_seconds']:.2f}" if row['conversion_duration_seconds'] else '',
                row['error_message'] or ''
            ])

    print(f"✓ Exported {len(rows)} records to: {output_file}")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    # Initialize database
    db_path = Path("output/conversion_history.db")
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("   Run a conversion first to create the database.")
        sys.exit(1)

    db = ConversionDatabase(str(db_path))

    try:
        if command == "list-batches":
            list_batches(db)

        elif command == "batch-info":
            if len(sys.argv) < 3:
                print("Usage: python db_query.py batch-info <batch_id>")
                sys.exit(1)
            batch_info(db, sys.argv[2])

        elif command == "page-history":
            if len(sys.argv) < 4:
                print("Usage: python db_query.py page-history <wiki_url> <page_id>")
                sys.exit(1)
            page_history(db, sys.argv[2], sys.argv[3])

        elif command == "failed-pages":
            if len(sys.argv) < 3:
                print("Usage: python db_query.py failed-pages <batch_id>")
                sys.exit(1)
            failed_pages(db, sys.argv[2])

        elif command == "broken-images":
            broken_images(db)

        elif command == "accessibility-trends":
            if len(sys.argv) < 4:
                print("Usage: python db_query.py accessibility-trends <wiki_url> <page_id>")
                sys.exit(1)
            accessibility_trends(db, sys.argv[2], sys.argv[3])

        elif command == "export-csv":
            if len(sys.argv) < 4:
                print("Usage: python db_query.py export-csv <batch_id> <output_file>")
                sys.exit(1)
            export_csv(db, sys.argv[2], sys.argv[3])

        else:
            print(f"❌ Unknown command: {command}")
            print(__doc__)
            sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
