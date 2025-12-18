#!/usr/bin/env python3
"""
Regenerate comprehensive image report from all images in database.

This script rebuilds the image_report.html with data from all conversion batches,
not just the latest batch. Useful when reports get out of sync or need updating.

Usage:
    python regenerate_image_report.py              # Uses default database
    python regenerate_image_report.py --db <path>  # Use specific database
"""

import argparse
import sys
from pathlib import Path
from wikiaccess.database import ConversionDatabase
from wikiaccess.image_reporting import ImageReportGenerator


def main():
    """Regenerate image report from all images in database."""
    parser = argparse.ArgumentParser(
        description='Regenerate comprehensive image report from all batches'
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

    args = parser.parse_args()

    # Connect to database
    try:
        db = ConversionDatabase(args.db)
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return 1

    try:
        # Query all images from database
        print(f"\n{'='*70}")
        print(f"Regenerating Comprehensive Image Report")
        print(f"{'='*70}\n")

        all_images = db.conn.execute('''
            SELECT page_id, type, source_url, local_filename, status,
                   file_size, dimensions, alt_text, error_message, downloaded_at
            FROM images
            ORDER BY downloaded_at DESC
        ''').fetchall()

        print(f"Found {len(all_images)} total images in database")

        # Convert database rows to image_details format
        comprehensive_image_details = []
        output_dir_path = Path(args.output_dir)
        for img_row in all_images:
            local_filename = img_row[3]
            local_path = str(output_dir_path / 'images' / local_filename) if local_filename else None

            img_dict = {
                'page_id': img_row[0],
                'type': img_row[1],
                'source_url': img_row[2],
                'local_filename': local_filename,
                'local_path': local_path,
                'status': img_row[4],
                'file_size': img_row[5],
                'dimensions': img_row[6],
                'alt_text': img_row[7],
                'error_message': img_row[8],
                'downloaded_at': img_row[9]
            }
            comprehensive_image_details.append(img_dict)

        # Generate the comprehensive image report
        if comprehensive_image_details:
            image_reporter = ImageReportGenerator(str(args.output_dir))
            image_report_path = image_reporter.generate_image_report(
                comprehensive_image_details
            )
            print(f"✓ Image report regenerated: {image_report_path}")
            print(f"  Total images: {len(comprehensive_image_details)}")

            # Count by status
            status_counts = {}
            for img in comprehensive_image_details:
                status = img.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

            print(f"\n  Image status breakdown:")
            for status, count in sorted(status_counts.items()):
                print(f"    - {status}: {count}")

            print(f"\n✓ Comprehensive image report regenerated successfully")
            return 0
        else:
            print(f"✗ No images found in database")
            return 1

    except Exception as e:
        print(f"✗ Error regenerating image report: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
