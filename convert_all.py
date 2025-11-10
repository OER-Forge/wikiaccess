#!/usr/bin/env python3#!/usr/bin/env python3

""""""

Backward compatibility script for convert_all.pyUnified DokuWiki Converter with Accessibility Checking

This script maintains the original interface while using the new package structure.

"""Converts DokuWiki pages to both HTML and DOCX with full accessibility compliance checking

"""

import sys

from pathlib import Pathimport sys

from wikiaccess.unified import convert_multiple_pagesimport argparse

import argparsefrom pathlib import Path

from scraper import DokuWikiHTTPClient

from html_converter import HTMLConverter

def main():from convert import EnhancedDokuWikiConverter

    """Main CLI entry point matching original convert_all.py interface"""from a11y_checker import AccessibilityChecker

    parser = argparse.ArgumentParser(from reporter import ReportGenerator

        description='Convert DokuWiki pages to both HTML and DOCX with accessibility compliance checking'

    )

    def main():

    parser.add_argument('wiki_url', help='Base URL of the DokuWiki site')    """Main CLI entry point"""

    parser.add_argument('page_names', nargs='+', help='Names of wiki pages to convert')    parser = argparse.ArgumentParser(

    parser.add_argument('-o', '--output-dir', default='output', help='Output directory')        description='Convert DokuWiki pages to accessible HTML and Word documents',

            formatter_class=argparse.RawDescriptionHelpFormatter,

    args = parser.parse_args()        epilog="""

    Examples:

    try:  # Convert to both HTML and DOCX

        results = convert_multiple_pages(  %(prog)s "https://wiki.com/doku.php?id=page" -o output/mypage

            wiki_url=args.wiki_url,  

            page_names=args.page_names,  # HTML only

            output_dir=args.output_dir,  %(prog)s "https://wiki.com/doku.php?id=page" --html-only

            formats=['html', 'docx'],  

            check_accessibility=True  # DOCX only

        )  %(prog)s "https://wiki.com/doku.php?id=page" --docx-only

          

        # Display results in original format  # With authentication

        for page_name, result in results.items():  %(prog)s "https://wiki.com/doku.php?id=page" -u username -p password

            if 'error' in result:  

                print(f"Error converting {page_name}: {result['error']}")  # Skip accessibility checking

            else:  %(prog)s "https://wiki.com/doku.php?id=page" --no-check

                print(f"Successfully converted: {page_name}")        """

                    )

        print("\nConversion complete. Check the accessibility report for WCAG compliance details.")    

            parser.add_argument('url', help='DokuWiki page URL')

    except Exception as e:    parser.add_argument('-o', '--output', default='output',

        print(f"Error: {e}")                       help='Output directory (default: output)')

        sys.exit(1)    parser.add_argument('-t', '--title', help='Document title')

    parser.add_argument('-l', '--language', default='en',

                       help='Document language (default: en)')

if __name__ == '__main__':    parser.add_argument('-u', '--username', help='Wiki username')

    main()    parser.add_argument('-p', '--password', help='Wiki password')
    parser.add_argument('--html-only', action='store_true',
                       help='Generate HTML only')
    parser.add_argument('--docx-only', action='store_true',
                       help='Generate DOCX only')
    parser.add_argument('--no-check', action='store_true',
                       help='Skip accessibility checking')
    
    args = parser.parse_args()
    
    # Setup output directories
    output_base = Path(args.output)
    html_dir = output_base / 'html'
    docx_dir = output_base / 'docx'
    
    # Initialize client
    client = DokuWikiHTTPClient(args.url, username=args.username, password=args.password)
    
    print("\n" + "=" * 70)
    print("🔄 DokuWiki to Accessible Documents Converter")
    print("=" * 70)
    print(f"Source: {args.url}")
    print(f"Output: {output_base}")
    print(f"Formats: {'HTML' if not args.docx_only else ''} {'DOCX' if not args.html_only else ''}")
    print("=" * 70)
    
    results = []
    
    # Convert to HTML
    if not args.docx_only:
        print("\n📝 GENERATING HTML...")
        html_converter = HTMLConverter(client, output_dir=str(html_dir))
        try:
            html_path, html_stats = html_converter.convert_url(
                args.url,
                document_title=args.title,
                language=args.language
            )
            
            if html_path:
                results.append(('html', html_path, html_stats))
                print(f"✅ HTML generated: {html_path}")
        except Exception as e:
            print(f"❌ HTML conversion failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Convert to DOCX
    if not args.html_only:
        print("\n📄 GENERATING DOCX...")
        docx_converter = EnhancedDokuWikiConverter(client, temp_dir=str(docx_dir / 'temp'))
        try:
            docx_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine output filename
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(args.url)
            page_id = parse_qs(parsed_url.query).get('id', ['page'])[0]
            docx_filename = page_id.replace(':', '_') + '.docx'
            docx_path = docx_dir / docx_filename
            
            success = docx_converter.convert_url(
                args.url,
                output_path=str(docx_path),
                document_title=args.title,
                language=args.language
            )
            
            if success:
                results.append(('docx', str(docx_path), {'equations': docx_converter.equation_count}))
                print(f"✅ DOCX generated: {docx_path}")
        except Exception as e:
            print(f"❌ DOCX conversion failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Accessibility checking
    if not args.no_check and results:
        print("\n♿ CHECKING ACCESSIBILITY...")
        checker = AccessibilityChecker()
        reporter = ReportGenerator(str(output_base))
        
        for file_type, file_path, stats in results:
            print(f"\n  Analyzing {file_type.upper()}: {Path(file_path).name}")
            
            if file_type == 'html':
                report = checker.check_html(file_path)
            else:
                report = checker.check_docx(file_path)
            
            print(f"    WCAG AA Score:  {report['score_aa']}%")
            print(f"    WCAG AAA Score: {report['score_aaa']}%")
            print(f"    AA Issues:      {len(report['issues_aa'])}")
            print(f"    AAA Issues:     {len(report['issues_aaa'])}")
            print(f"    Warnings:       {len(report['warnings'])}")
            
            reporter.add_report(report)
            detail_path = reporter.generate_detailed_report(report)
            print(f"    📋 Detail report: {detail_path}")
        
        # Generate dashboard
        dashboard_path = reporter.generate_dashboard()
        
        print("\n" + "=" * 70)
        print("✅ CONVERSION COMPLETE")
        print("=" * 70)
        
        # Summary
        for file_type, file_path, stats in results:
            print(f"\n{file_type.upper()}: {file_path}")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        print(f"\n📊 Accessibility Dashboard: {dashboard_path}")
        print("\nNext steps:")
        print("  1. Open HTML in browser to verify MathJax equations")
        print("  2. Open DOCX in Word to verify MathML equations")
        print("  3. Review accessibility report for any issues")
        print("  4. Test with screen readers (NVDA, JAWS, VoiceOver)")
        
    else:
        print("\n" + "=" * 70)
        print("✅ CONVERSION COMPLETE (no accessibility check)")
        print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
