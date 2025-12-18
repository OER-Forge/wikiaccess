#!/usr/bin/env python3
"""
Convert approved discovered pages.

Converts all pages with discovery_status='approved' from the database.
After successful conversion, status is updated to 'converted'.

Usage:
    python convert_approved.py                    # Convert all approved
    python convert_approved.py --max-depth 1      # Only depth 1 pages
    python convert_approved.py --dry-run           # Show what would convert
    python convert_approved.py --format html       # Only HTML format
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from wikiaccess.database import ConversionDatabase
from wikiaccess.unified import convert_multiple_pages


def main():
    """Convert approved discovered pages."""
    parser = argparse.ArgumentParser(
        description='Convert approved discovered pages'
    )
    parser.add_argument(
        '--db',
        default='output/conversion_history.db',
        help='Path to database'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for conversions'
    )
    parser.add_argument(
        '--wiki-url',
        default='https://msuperl.org/wikis/pcubed',
        help='Wiki base URL'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=None,
        help='Maximum discovery depth to include'
    )
    parser.add_argument(
        '--format',
        default=None,
        choices=['html', 'docx', 'both'],
        help='Output format(s)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without converting'
    )
    parser.add_argument(
        '--no-accessibility',
        action='store_true',
        help='Skip accessibility checking'
    )
    parser.add_argument(
        '--no-discovery',
        action='store_true',
        help='Disable auto-discovery for converted pages'
    )

    args = parser.parse_args()

    # Connect to database
    try:
        db = ConversionDatabase(args.db)
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return 1

    # Get approved pages
    try:
        approved_pages = db.get_approved_pages_for_conversion(args.max_depth)
    except Exception as e:
        print(f"✗ Error getting approved pages: {e}")
        db.close()
        return 1

    if not approved_pages:
        print("✓ No approved pages to convert")
        db.close()
        return 0

    print(f"\n{'='*70}")
    print(f"Converting Approved Discovered Pages")
    print(f"{'='*70}\n")

    print(f"Found {len(approved_pages)} approved pages for conversion")

    # Apply filters
    if args.max_depth is not None:
        print(f"  Limited to depth: {args.max_depth}")

    print(f"\nPages to convert:")
    for i, page_id in enumerate(approved_pages, 1):
        print(f"  {i}. {page_id}")

    # Dry run?
    if args.dry_run:
        print(f"\n✓ Dry run complete. Would convert {len(approved_pages)} pages")
        db.close()
        return 0

    # Confirm conversion
    confirm = input(f"\nConvert {len(approved_pages)} pages? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        db.close()
        return 1

    # Prepare conversion parameters
    formats = args.format
    if formats == 'html':
        formats = ['html']
    elif formats == 'docx':
        formats = ['docx']
    else:  # both or None
        formats = ['html', 'docx']

    # Create new batch for discovered pages conversion
    batch_id = f"discovered_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db.start_batch(batch_id, args.wiki_url)

    try:
        print(f"\nStarting conversion batch: {batch_id}\n")

        # Convert pages
        results = convert_multiple_pages(
            wiki_url=args.wiki_url,
            page_names=approved_pages,
            output_dir=args.output_dir,
            formats=formats,
            check_accessibility=not args.no_accessibility,
            use_database=True,
            skip_recent=False,  # Don't skip - we want to convert approved pages
            enable_discovery=not args.no_discovery,
            max_discovery_depth=2
        )

        # Update conversion status in database
        print(f"\n{'='*70}")
        print(f"Updating Discovery Status")
        print(f"{'='*70}\n")

        converted_count = 0
        failed_count = 0

        for page_id, result in results.items():
            # Skip if page was skipped
            if result.get('skipped', False):
                continue

            # Check if conversion had an error
            if 'error' in result:
                failed_count += 1
                error_msg = result['error']
                print(f"✗ {page_id}: conversion failed ({error_msg})")
                continue

            # If no error and not skipped, it was successful
            try:
                db.mark_discovered_as_converted(page_id, batch_id)
                converted_count += 1
                print(f"✓ {page_id}: converted")
            except Exception as e:
                print(f"⚠️  {page_id}: error updating status - {e}")
                failed_count += 1

        print(f"\n{'='*70}")
        print(f"Conversion Summary")
        print(f"{'='*70}")
        print(f"  Converted: {converted_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total: {converted_count + failed_count}")

        if converted_count > 0:
            print(f"\n✓ Successfully converted {converted_count} approved pages")
        if failed_count > 0:
            print(f"⚠️  {failed_count} pages failed to convert")

        return 0 if failed_count == 0 else 1

    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Conversion error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
