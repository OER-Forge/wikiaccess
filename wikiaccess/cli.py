"""
WikiAccess Command Line Interface

Provides command-line access to WikiAccess functionality.
"""

import argparse
import sys
from pathlib import Path
from .unified import convert_wiki_page, convert_multiple_pages


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Transform DokuWiki pages into accessible documents'
    )
    
    parser.add_argument(
        'wiki_url',
        help='Base URL of the DokuWiki site'
    )
    
    parser.add_argument(
        'pages',
        nargs='+',
        help='Wiki page names to convert (space separated)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output',
        help='Output directory (default: output)'
    )
    
    parser.add_argument(
        '-f', '--formats',
        nargs='+',
        choices=['html', 'docx'],
        default=['html', 'docx'],
        help='Output formats (default: both html and docx)'
    )
    
    parser.add_argument(
        '--no-accessibility',
        action='store_true',
        help='Skip accessibility checking'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='WikiAccess 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        results = None
        result = None
        
        if len(args.pages) == 1:
            # Single page conversion
            result = convert_wiki_page(
                wiki_url=args.wiki_url,
                page_name=args.pages[0],
                output_dir=args.output,
                formats=args.formats,
                check_accessibility=not args.no_accessibility
            )
            
            print(f"✅ Successfully converted '{args.pages[0]}'")
            for format_type, format_result in result.items():
                if format_type in ['html', 'docx'] and 'file_path' in format_result:
                    print(f"   {format_type.upper()}: {format_result['file_path']}")
                    
        else:
            # Multiple pages conversion
            results = convert_multiple_pages(
                wiki_url=args.wiki_url,
                page_names=args.pages,
                output_dir=args.output,
                formats=args.formats,
                check_accessibility=not args.no_accessibility
            )
            
            for page_name, page_result in results.items():
                if 'error' in page_result:
                    print(f"❌ Failed to convert '{page_name}': {page_result['error']}")
                else:
                    print(f"✅ Successfully converted '{page_name}'")
                    for format_type, format_result in page_result.items():
                        if format_type in ['html', 'docx'] and 'file_path' in format_result:
                            print(f"   {format_type.upper()}: {format_result['file_path']}")
        
        # Show accessibility report if generated
        if result and 'accessibility_report' in result:
            print(f"\n📊 Accessibility report: {result['accessibility_report']}")
        elif results:
            # Check if any results have accessibility reports
            for page_result in results.values():
                if 'accessibility_report' in page_result:
                    print(f"\n📊 Accessibility report: {page_result['accessibility_report']}")
                    break
                    
    except KeyboardInterrupt:
        print("\n🛑 Conversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()