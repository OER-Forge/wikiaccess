#!/usr/bin/env python3
"""
Resolve broken links that now point to converted pages.

After discovering and converting new pages, many broken links will now point to
pages that exist in the database. This script updates those link statuses from
'missing' to 'found'.

Usage:
    python resolve_broken_links.py              # Uses default database
    python resolve_broken_links.py --db <path>  # Use specific database
"""

import argparse
import sys
from pathlib import Path
from wikiaccess.database import ConversionDatabase


def main():
    """Resolve broken links that now point to converted pages."""
    parser = argparse.ArgumentParser(
        description='Resolve broken links that now point to converted pages'
    )
    parser.add_argument(
        '--db',
        default='output/conversion_history.db',
        help='Path to database'
    )

    args = parser.parse_args()

    # Connect to database
    try:
        db = ConversionDatabase(args.db)
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return 1

    try:
        print(f"\n{'='*70}")
        print(f"Resolving Broken Links to Converted Pages")
        print(f"{'='*70}\n")

        # Get count before
        before_broken = db.conn.execute('''
            SELECT COUNT(*) FROM links WHERE resolution_status='missing' AND link_type='internal'
        ''').fetchone()[0]

        print(f"Before: {before_broken} broken links")

        # Resolve converted links
        resolved_count = db.resolve_converted_links()

        # Get count after
        after_broken = db.conn.execute('''
            SELECT COUNT(*) FROM links WHERE resolution_status='missing' AND link_type='internal'
        ''').fetchone()[0]

        print(f"Resolved: {resolved_count} links that now point to converted pages")
        print(f"After: {after_broken} broken links remaining")
        print(f"\n✓ Link resolution complete!")

        # Show what's still broken
        print(f"\n{'='*70}")
        print(f"Remaining Broken Links Summary")
        print(f"{'='*70}\n")

        remaining_broken = db.get_all_broken_links()
        print(f"Total unique broken link targets: {len(remaining_broken)}")
        print(f"Total broken link references: {sum(l['reference_count'] for l in remaining_broken)}")

        # Show top remaining broken links
        print(f"\nTop remaining missing pages:")
        for link in remaining_broken[:10]:
            print(f"  - {link['target_page_id']}: {link['reference_count']} references")

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
