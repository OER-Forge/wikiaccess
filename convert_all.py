#!/usr/bin/env python3
"""
Backward compatibility script for convert_all.py

This script maintains the original interface while using the new package structure.
Converts DokuWiki pages to both HTML and DOCX with full accessibility compliance checking.
"""

import sys
import argparse
from pathlib import Path
from wikiaccess import convert_multiple_pages


def main():
    """Main CLI entry point matching original convert_all.py interface"""
    parser = argparse.ArgumentParser(
        description='Convert DokuWiki pages to both HTML and DOCX with accessibility compliance checking'
    )

    parser.add_argument('wiki_url', help='Base URL of the DokuWiki site')
    parser.add_argument('page_names', nargs='+', help='Names of wiki pages to convert')
    parser.add_argument('-o', '--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--html-only', action='store_true', help='Generate HTML only')
    parser.add_argument('--docx-only', action='store_true', help='Generate DOCX only')
    parser.add_argument('--no-check', action='store_true', help='Skip accessibility checking')

    args = parser.parse_args()

    # Determine output formats
    if args.html_only:
        formats = ['html']
    elif args.docx_only:
        formats = ['docx']
    else:
        formats = ['html', 'docx']

    try:
        print(f"\nConverting {len(args.page_names)} page(s) from {args.wiki_url}")
        print(f"Output directory: {args.output_dir}")
        print(f"Formats: {', '.join(formats)}")
        print(f"Accessibility checking: {'disabled' if args.no_check else 'enabled'}\n")

        results = convert_multiple_pages(
            wiki_url=args.wiki_url,
            page_names=args.page_names,
            output_dir=args.output_dir,
            formats=formats,
            check_accessibility=not args.no_check
        )

        # Display results
        print("\n" + "=" * 70)
        print("CONVERSION RESULTS")
        print("=" * 70)

        for page_name, result in results.items():
            if 'error' in result:
                print(f"\n❌ Error converting {page_name}: {result['error']}")
            else:
                print(f"\n✅ Successfully converted: {page_name}")

                if 'html' in result:
                    print(f"   HTML: {result['html']['file_path']}")

                if 'docx' in result:
                    print(f"   DOCX: {result['docx']['file_path']}")

                if 'accessibility' in result:
                    accessibility = result['accessibility']
                    if 'html' in accessibility:
                        html_acc = accessibility['html']
                        print(f"   HTML Accessibility Score: {html_acc.get('score_aa', 'N/A')}%")
                    if 'docx' in accessibility:
                        docx_acc = accessibility['docx']
                        print(f"   DOCX Accessibility Score: {docx_acc.get('score_aa', 'N/A')}%")

        # Show accessibility report path if available
        if not args.no_check:
            print("\n" + "=" * 70)
            print("Check the accessibility reports in:")
            print(f"  {Path(args.output_dir) / 'reports'}/")
            print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
