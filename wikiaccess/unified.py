"""
WikiAccess Unified Interface

High-level convenience functions for common WikiAccess operations.
These provide simple interfaces for the most common use cases.

Uses Markdown as intermediate format:
1. DokuWiki → Markdown (simple parser)
2. Markdown → HTML/DOCX (pandoc)
3. Check accessibility
4. Generate reports
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import time
from .scraper import DokuWikiHTTPClient
from .markdown_converter import MarkdownConverter
from .accessibility import AccessibilityChecker
from .reporting import ReportGenerator
from .static_helper import copy_static_files
from .image_reporting import ImageReportGenerator
from .hub_reporting import HubReportGenerator
from .database import ConversionDatabase
from .link_rewriter import LinkRewriter
from .discovery import PageDiscoveryEngine


def convert_wiki_page(
    wiki_url: str,
    page_name: str,
    output_dir: Optional[str] = None,
    formats: Optional[list] = None,
    check_accessibility: bool = True,
    use_database: bool = True,
    batch_id: Optional[str] = None,
    include_accessibility_toolbar: bool = True
) -> Dict[str, Any]:
    """
    Convert a single DokuWiki page to accessible documents via Markdown.

    Output structure:
        output/
        ├── markdown/
        │   └── page_name.md
        ├── images/
        │   └── [downloaded images + YouTube thumbnails]
        ├── html/
        │   └── page_name.html
        ├── docx/
        │   └── page_name.docx
        └── reports/
            ├── accessibility_report.html
            └── page_name_accessibility.html

    Args:
        wiki_url: Base URL of the DokuWiki site
        page_name: Name of the wiki page to convert
        output_dir: Directory to save outputs (defaults to 'output')
        formats: List of formats to generate ['html', 'docx'] (defaults to both)
        check_accessibility: Whether to run accessibility checks
        use_database: Whether to use database for tracking (defaults to True)
        batch_id: Optional batch identifier for grouping related conversions
        include_accessibility_toolbar: Whether to include toolbar in HTML (defaults to True)

    Returns:
        Dictionary with paths to generated files and accessibility results
    """
    if output_dir is None:
        output_dir = "output"

    if formats is None:
        formats = ['html', 'docx']

    if batch_id is None:
        batch_id = f"single_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Initialize database if enabled
    db = None
    if use_database:
        db_path = output_path / "conversion_history.db"
        db = ConversionDatabase(str(db_path))

        # Check if recently converted (skip if within 1 hour)
        if db.was_recently_converted(wiki_url, page_name, hours=1):
            print(f"⏭️  Skipping {page_name} (converted within last hour)")
            return {'skipped': True, 'reason': 'recently_converted'}

        db.start_batch(batch_id, wiki_url)

    # Initialize components
    client = DokuWikiHTTPClient(wiki_url)
    converter = MarkdownConverter(client, output_dir, include_accessibility_toolbar)
    results = {}

    # Track conversion time
    start_time = time.time()
    conversion_status = 'SUCCESS'
    error_message = None

    try:
        # Convert DokuWiki → Markdown → HTML/DOCX
        page_url = f"{wiki_url}/doku.php?id={page_name}"
        html_path, docx_path, stats = converter.convert_url(page_url)
    except Exception as e:
        conversion_status = 'FAILED'
        error_message = str(e)
        html_path = None
        docx_path = None
        stats = {}
        raise
    finally:
        conversion_duration = time.time() - start_time
    
    if html_path:
        results['html'] = {
            'file_path': html_path,
            'stats': stats
        }
    
    if docx_path:
        results['docx'] = {
            'file_path': docx_path,
            'stats': stats
        }
    
    # Run accessibility checks if requested
    if check_accessibility:
        checker = AccessibilityChecker()
        accessibility_results = {}

        if html_path:
            html_accessibility = checker.check_html(html_path)
            accessibility_results['html'] = html_accessibility

        if docx_path:
            docx_accessibility = checker.check_docx(docx_path)
            accessibility_results['docx'] = docx_accessibility

        results['accessibility'] = accessibility_results

        # Generate accessibility report in shared reports folder
        if accessibility_results:
            page_display_name = page_name.replace(':', '_')
            reports_dir = output_path / 'reports'
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Copy static CSS files to reports directory
            copy_static_files(str(output_path))

            reporter = ReportGenerator(str(reports_dir))

            html_report = accessibility_results.get('html', {})
            docx_report = accessibility_results.get('docx', {})

            reporter.add_page_reports(
                page_display_name,
                html_report,
                docx_report,
                results.get('html', {}).get('stats', {}),
                results.get('docx', {}).get('stats', {})
            )
            reporter.generate_detailed_reports()
            dashboard_path = reporter.generate_dashboard()
            results['accessibility_report'] = dashboard_path

    # Generate image report if images were processed
    if converter.image_details:
        reports_dir = output_path / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)

        image_reporter = ImageReportGenerator(str(output_dir))
        image_report_path = image_reporter.generate_image_report(converter.image_details)
        results['image_report'] = image_report_path
        print(f"\n📸 Image Report: {image_report_path}")

    # Generate landing hub (index.html) if we have reports
    if check_accessibility and results.get('accessibility'):
        hub_generator = HubReportGenerator(str(output_dir))
        page_display_name = page_name.replace(':', '_')

        # Prepare page_reports dict for hub generator
        page_reports = {
            page_display_name: {
                'html': results['accessibility'].get('html', {}),
                'docx': results['accessibility'].get('docx', {}),
                'html_stats': results.get('html', {}).get('stats', {}),
                'docx_stats': results.get('docx', {}).get('stats', {})
            }
        }

        hub_path = hub_generator.generate_hub(page_reports, converter.image_details)
        results['hub_report'] = hub_path

    # Store page conversion in database
    if db:
        page_data = {
            'wiki_url': wiki_url,
            'page_id': page_name,
            'batch_id': batch_id,
            'conversion_status': conversion_status,
            'markdown_path': str(output_path / 'markdown' / f"{page_name.replace(':', '_')}.md"),
            'html_path': html_path,
            'docx_path': docx_path,
            'html_wcag_aa_score': results.get('accessibility', {}).get('html', {}).get('score_aa'),
            'html_wcag_aaa_score': results.get('accessibility', {}).get('html', {}).get('score_aaa'),
            'docx_wcag_aa_score': results.get('accessibility', {}).get('docx', {}).get('score_aa'),
            'docx_wcag_aaa_score': results.get('accessibility', {}).get('docx', {}).get('score_aaa'),
            'image_count': stats.get('images', 0),
            'image_success_count': stats.get('images_success', 0),
            'image_failed_count': stats.get('images_failed', 0),
            'conversion_duration_seconds': conversion_duration,
            'error_message': error_message
        }
        db.add_page_conversion(page_data)

        # Store image details
        for img in converter.image_details:
            img_data = {
                'page_id': page_name,
                'batch_id': batch_id,
                'type': img.get('type', 'wiki_image'),
                'source_url': img.get('source_url'),
                'local_filename': img.get('local_filename'),
                'status': img.get('status'),
                'file_size': img.get('file_size'),
                'dimensions': img.get('dimensions'),
                'alt_text': img.get('alt_text'),
                'alt_text_quality': 'missing' if not img.get('alt_text') else 'manual',
                'error_message': img.get('error_message')
            }
            db.add_image(img_data)

        # Store accessibility issues
        if check_accessibility and results.get('accessibility'):
            for format_type in ['html', 'docx']:
                format_upper = format_type.upper()
                accessibility = results['accessibility'].get(format_type, {})

                for level in ['AA', 'AAA']:
                    issues_key = f'issues_{level.lower()}'
                    for issue in accessibility.get(issues_key, []):
                        # Handle both dict and string issue formats
                        if isinstance(issue, dict):
                            issue_data = {
                                'page_id': page_name,
                                'batch_id': batch_id,
                                'format': format_upper,
                                'level': level,
                                'issue_code': issue.get('code', 'unknown'),
                                'issue_message': issue.get('message', ''),
                                'element_selector': issue.get('selector', '')
                            }
                        else:
                            # Issue is a string
                            issue_data = {
                                'page_id': page_name,
                                'batch_id': batch_id,
                                'format': format_upper,
                                'level': level,
                                'issue_code': 'unknown',
                                'issue_message': str(issue),
                                'element_selector': ''
                            }
                        db.add_accessibility_issue(issue_data)

        # Complete batch
        batch_stats = {
            'total_pages': 1,
            'successful_pages': 1 if conversion_status == 'SUCCESS' else 0,
            'failed_pages': 1 if conversion_status == 'FAILED' else 0,
            'total_images': stats.get('images', 0),
            'failed_images': stats.get('images_failed', 0)
        }
        db.complete_batch(batch_id, batch_stats)
        db.close()

    return results


def convert_multiple_pages(
    wiki_url: str,
    page_names: list,
    output_dir: Optional[str] = None,
    formats: Optional[list] = None,
    check_accessibility: bool = True,
    use_database: bool = True,
    skip_recent: bool = True,
    include_accessibility_toolbar: bool = True,
    enable_discovery: bool = True,
    max_discovery_depth: int = 2
) -> Dict[str, Dict[str, Any]]:
    """
    Convert multiple DokuWiki pages to accessible documents.

    Output structure:
        output/
        ├── markdown/
        │   ├── page1.md
        │   └── page2.md
        ├── images/
        │   ├── page1_img.png
        │   ├── page2_img.jpg
        │   └── youtube_[id].jpg
        ├── html/
        │   ├── page1.html
        │   └── page2.html
        ├── docx/
        │   ├── page1.docx
        │   └── page2.docx
        └── reports/
            ├── accessibility_report.html (combined)
            ├── page1_accessibility.html
            └── page2_accessibility.html

    Args:
        wiki_url: Base URL of the DokuWiki site
        page_names: List of page names to convert
        output_dir: Directory to save outputs (defaults to 'output')
        formats: List of formats to generate (defaults to both)
        check_accessibility: Whether to run accessibility checks
        use_database: Whether to use database for tracking (defaults to True)
        skip_recent: Skip pages converted within last hour (defaults to True)
        include_accessibility_toolbar: Whether to include toolbar in HTML (defaults to True)

    Returns:
        Dictionary mapping page names to their conversion results
    """
    if output_dir is None:
        output_dir = "output"

    if formats is None:
        formats = ['html', 'docx']

    # Collect all page results for combined report
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Initialize database if enabled
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db = None
    if use_database:
        db_path = output_path / "conversion_history.db"
        db = ConversionDatabase(str(db_path))
        db.start_batch(batch_id, wiki_url)

    client = DokuWikiHTTPClient(wiki_url)
    converter = MarkdownConverter(client, output_dir, include_accessibility_toolbar)

    page_results = {}
    # Create separate reporter for combined report (if multiple pages)
    combined_reporter = ReportGenerator(str(output_path / 'reports')) if check_accessibility else None

    # Copy static CSS files to reports directory (once at start)
    if combined_reporter:
        (output_path / 'reports').mkdir(parents=True, exist_ok=True)
        copy_static_files(str(output_path))

    # Track batch statistics
    total_pages = len(page_names)
    successful_pages = 0
    failed_pages = 0
    skipped_pages = 0
    total_images = 0
    failed_images = 0

    for page_name in page_names:
        print(f"\n{'='*70}\nPage: {page_name}\n{'='*70}")

        # Check if recently converted (skip if requested)
        if db and skip_recent and db.was_recently_converted(wiki_url, page_name, hours=1):
            print(f"⏭️  Skipping {page_name} (converted within last hour)")
            page_results[page_name] = {'skipped': True, 'reason': 'recently_converted'}
            skipped_pages += 1
            continue

        conversion_status = 'SUCCESS'
        error_message = None
        start_time = time.time()

        try:
            page_url = f"{wiki_url}/doku.php?id={page_name}"
            html_path, docx_path, stats = converter.convert_url(page_url)

            results = {
                'html': {'file_path': html_path, 'stats': stats} if html_path else None,
                'docx': {'file_path': docx_path, 'stats': stats} if docx_path else None
            }

            # Update batch stats
            total_images += stats.get('images', 0)
            failed_images += stats.get('images_failed', 0)

            # Check accessibility
            if check_accessibility:
                checker = AccessibilityChecker()
                accessibility_results = {}

                if html_path:
                    html_accessibility = checker.check_html(html_path)
                    accessibility_results['html'] = html_accessibility

                if docx_path:
                    docx_accessibility = checker.check_docx(docx_path)
                    accessibility_results['docx'] = docx_accessibility

                results['accessibility'] = accessibility_results

                # Add to combined reporter
                if combined_reporter:
                    page_display_name = page_name.replace(':', '_')
                    combined_reporter.add_page_reports(
                        page_display_name,
                        accessibility_results.get('html', {}),
                        accessibility_results.get('docx', {}),
                        stats,
                        stats
                    )

            page_results[page_name] = results
            successful_pages += 1
            print(f"✓ Successfully converted: {page_name}")

        except Exception as e:
            conversion_status = 'FAILED'
            error_message = str(e)
            page_results[page_name] = {'error': str(e)}
            failed_pages += 1
            html_path = None
            docx_path = None
            stats = {}
            print(f"✗ Failed to convert {page_name}: {e}")

        finally:
            conversion_duration = time.time() - start_time

            # Store in database
            if db:
                page_data = {
                    'wiki_url': wiki_url,
                    'page_id': page_name,
                    'batch_id': batch_id,
                    'conversion_status': conversion_status,
                    'markdown_path': str(output_path / 'markdown' / f"{page_name.replace(':', '_')}.md"),
                    'html_path': html_path,
                    'docx_path': docx_path,
                    'html_wcag_aa_score': results.get('accessibility', {}).get('html', {}).get('score_aa') if conversion_status == 'SUCCESS' else None,
                    'html_wcag_aaa_score': results.get('accessibility', {}).get('html', {}).get('score_aaa') if conversion_status == 'SUCCESS' else None,
                    'docx_wcag_aa_score': results.get('accessibility', {}).get('docx', {}).get('score_aa') if conversion_status == 'SUCCESS' else None,
                    'docx_wcag_aaa_score': results.get('accessibility', {}).get('docx', {}).get('score_aaa') if conversion_status == 'SUCCESS' else None,
                    'image_count': stats.get('images', 0),
                    'image_success_count': stats.get('images_success', 0),
                    'image_failed_count': stats.get('images_failed', 0),
                    'conversion_duration_seconds': conversion_duration,
                    'error_message': error_message
                }
                db.add_page_conversion(page_data)

                # Store image details
                if conversion_status == 'SUCCESS':
                    for img in converter.image_details:
                        if img.get('page_id') == page_name or not img.get('page_id'):
                            img_data = {
                                'page_id': page_name,
                                'batch_id': batch_id,
                                'type': img.get('type', 'wiki_image'),
                                'source_url': img.get('source_url'),
                                'local_filename': img.get('local_filename'),
                                'status': img.get('status'),
                                'file_size': img.get('file_size'),
                                'dimensions': img.get('dimensions'),
                                'alt_text': img.get('alt_text'),
                                'alt_text_quality': 'missing' if not img.get('alt_text') else 'manual',
                                'error_message': img.get('error_message')
                            }
                            db.add_image(img_data)

                    # Store accessibility issues
                    if check_accessibility and results.get('accessibility'):
                        for format_type in ['html', 'docx']:
                            format_upper = format_type.upper()
                            accessibility = results['accessibility'].get(format_type, {})

                            for level in ['AA', 'AAA']:
                                issues_key = f'issues_{level.lower()}'
                                for issue in accessibility.get(issues_key, []):
                                    # Handle both dict and string issue formats
                                    if isinstance(issue, dict):
                                        issue_data = {
                                            'page_id': page_name,
                                            'batch_id': batch_id,
                                            'format': format_upper,
                                            'level': level,
                                            'issue_code': issue.get('code', 'unknown'),
                                            'issue_message': issue.get('message', ''),
                                            'element_selector': issue.get('selector', '')
                                        }
                                    else:
                                        # Issue is a string
                                        issue_data = {
                                            'page_id': page_name,
                                            'batch_id': batch_id,
                                            'format': format_upper,
                                            'level': level,
                                            'issue_code': 'unknown',
                                            'issue_message': str(issue),
                                            'element_selector': ''
                                        }
                                    db.add_accessibility_issue(issue_data)
    
    # Generate combined report
    if check_accessibility and combined_reporter:
        print(f"\n{'='*70}\nGenerating Combined Accessibility Report\n{'='*70}")
        combined_reporter.generate_detailed_reports()
        dashboard = combined_reporter.generate_dashboard()
        print(f"\n📊 Combined Dashboard: {dashboard}")

        # Regenerate comprehensive accessibility report from ALL pages in database
        print(f"\n🔧 Regenerating comprehensive report... (db={db is not None}, combined_reporter pages={len(combined_reporter.page_reports)})")
        if db:
            try:
                reports_dir = Path(output_dir) / 'reports'
                reports_dir.mkdir(parents=True, exist_ok=True)

                # Create fresh reporter and load all pages from database
                comprehensive_reporter = ReportGenerator(str(reports_dir))
                all_pages = db.conn.execute('''
                    SELECT p.page_id, p.html_wcag_aa_score, p.html_wcag_aaa_score,
                           p.docx_wcag_aa_score, p.docx_wcag_aaa_score
                    FROM pages p
                    ORDER BY p.page_id
                ''').fetchall()

                print(f"\n  Building comprehensive report with {len(all_pages)} pages from database...")

                # Add all pages to the comprehensive report
                for page_row in all_pages:
                    page_id = page_row[0]
                    page_display_name = page_id.replace(':', '_')

                    # Build basic report structure from database
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

                # Generate the comprehensive report
                if all_pages:
                    comprehensive_reporter.generate_detailed_reports()
                    comprehensive_dashboard = comprehensive_reporter.generate_dashboard()
                    print(f"📊 Comprehensive Accessibility Dashboard (all {len(all_pages)} pages): {comprehensive_dashboard}")
            except Exception as e:
                print(f"⚠️  Warning: Could not regenerate comprehensive report: {e}")

    # Generate image report if images were processed
    if converter.image_details:
        print(f"\n{'='*70}\nGenerating Image Report\n{'='*70}")
        image_reporter = ImageReportGenerator(str(output_dir))
        image_report_path = image_reporter.generate_image_report(converter.image_details)
        print(f"\n📸 Image Report: {image_report_path}")

    # Rewrite internal links to point to local HTML files
    print(f"\n{'='*70}\nRewriting Internal Links\n{'='*70}")
    link_rewriter = LinkRewriter(wiki_url, output_dir, db if use_database else None)
    link_stats = link_rewriter.rewrite_all_links(batch_id)

    print(f"\nLink Rewriting Summary:")
    print(f"  Files processed: {link_stats['files_processed']}")
    print(f"  Links found: {link_stats['links_found']}")
    print(f"  Links rewritten: {link_stats['links_rewritten']}")
    print(f"  Broken links: {link_stats['links_broken']}")

    # Generate broken links report if there are any
    if link_stats['links_broken'] > 0 and db:
        page_names_list = list(page_results.keys())
        link_rewriter.generate_broken_links_report(batch_id, page_names_list)

    # Auto-discover new pages from broken links
    if link_stats['links_broken'] > 0 and db and enable_discovery:
        print(f"\n{'='*70}\nDiscovering New Pages\n{'='*70}")
        try:
            discovery_engine = PageDiscoveryEngine(db, wiki_url, max_discovery_depth)

            # Get current batch depth
            batch_info = db.get_batch_info(batch_id)
            current_depth = batch_info.get('discovery_depth', 0) if batch_info else 0

            # Don't discover beyond max depth
            if current_depth < max_discovery_depth:
                discovery_stats = discovery_engine.discover_from_batch(batch_id, current_depth)

                print(f"  New discoveries: {discovery_stats['new_discoveries']}")
                print(f"  Already known: {discovery_stats['already_known']}")
                print(f"  External links: {discovery_stats['external_links']}")

                if discovery_stats['new_discoveries'] > 0:
                    print(f"\n📋 Review discovered pages with: python review_discoveries.py")
                    discovery_engine.close()
            else:
                print(f"  Reached max discovery depth ({max_discovery_depth}), skipping")
        except Exception as e:
            print(f"⚠️  Discovery error: {e}")
            import traceback
            traceback.print_exc()

    # Generate landing hub (index.html) if we have reports
    if check_accessibility and combined_reporter:
        print(f"\n{'='*70}\nGenerating Landing Hub\n{'='*70}")
        hub_generator = HubReportGenerator(str(output_dir))

        # Prepare page_reports dict for hub generator
        page_reports = {}
        for page_name, results in page_results.items():
            if 'accessibility' in results:
                page_display_name = page_name.replace(':', '_')
                page_reports[page_display_name] = {
                    'html': results['accessibility'].get('html', {}),
                    'docx': results['accessibility'].get('docx', {}),
                    'html_stats': results.get('html', {}).get('stats', {}),
                    'docx_stats': results.get('docx', {}).get('stats', {})
                }

        if page_reports:
            hub_path = hub_generator.generate_hub(page_reports, converter.image_details, link_stats)
            print(f"\n🏠 Landing Hub: {hub_path}")

        # Regenerate landing hub with all pages from database (comprehensive version)
        if db:
            print(f"\n🔧 Regenerating landing hub with all pages from database...")
            try:
                comprehensive_hub_generator = HubReportGenerator(str(output_dir))

                # Query all pages from database
                all_pages_for_hub = db.conn.execute('''
                    SELECT p.page_id, p.html_wcag_aa_score, p.html_wcag_aaa_score,
                           p.docx_wcag_aa_score, p.docx_wcag_aaa_score
                    FROM pages p
                    ORDER BY p.page_id
                ''').fetchall()

                # Build page_reports dict with all pages
                comprehensive_page_reports = {}
                for page_row in all_pages_for_hub:
                    page_id = page_row[0]
                    page_display_name = page_id.replace(':', '_')
                    comprehensive_page_reports[page_display_name] = {
                        'html': {
                            'score_aa': page_row[1] or 0,
                            'score_aaa': page_row[2] or 0,
                        },
                        'docx': {
                            'score_aa': page_row[3] or 0,
                            'score_aaa': page_row[4] or 0,
                        }
                    }

                # Generate the comprehensive hub
                if comprehensive_page_reports:
                    comprehensive_hub_path = comprehensive_hub_generator.generate_hub(
                        comprehensive_page_reports,
                        converter.image_details,
                        link_stats
                    )
                    print(f"🏠 Landing Hub (comprehensive - {len(comprehensive_page_reports)} pages): {comprehensive_hub_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not regenerate comprehensive landing hub: {e}")

        # Regenerate image report with all images from database (comprehensive version)
        print(f"\n🔧 Regenerating image report with all images from database...")
        try:
            comprehensive_image_reporter = ImageReportGenerator(str(output_dir))

            # Query all images from database
            all_images = db.conn.execute('''
                SELECT page_id, type, source_url, local_filename, status,
                       file_size, dimensions, alt_text, error_message, downloaded_at
                FROM images
                ORDER BY downloaded_at DESC
            ''').fetchall()

            # Convert database rows to image_details format
            comprehensive_image_details = []
            output_path = Path(output_dir)
            for img_row in all_images:
                local_filename = img_row[3]
                local_path = str(output_path / 'images' / local_filename) if local_filename else None

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
                comprehensive_image_report_path = comprehensive_image_reporter.generate_image_report(
                    comprehensive_image_details
                )
                print(f"📸 Image Report (comprehensive - {len(comprehensive_image_details)} images): {comprehensive_image_report_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not regenerate comprehensive image report: {e}")

    # Complete batch in database
    if db:
        batch_stats = {
            'total_pages': total_pages - skipped_pages,
            'successful_pages': successful_pages,
            'failed_pages': failed_pages,
            'total_images': total_images,
            'failed_images': failed_images
        }
        db.complete_batch(batch_id, batch_stats)

        print(f"\n{'='*70}\nBatch Summary (ID: {batch_id})\n{'='*70}")
        print(f"Total pages: {total_pages}")
        print(f"Successful: {successful_pages}")
        print(f"Failed: {failed_pages}")
        print(f"Skipped: {skipped_pages}")
        print(f"Total images: {total_images}")
        print(f"Failed images: {failed_images}")

        db.close()

    return page_results