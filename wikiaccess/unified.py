#!/usr/bin/env python3
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
from .conversion_orchestrator import ConversionOrchestrator
from .discovery_orchestrator import DiscoveryOrchestrator
from .accessibility_handler import AccessibilityIssueHandler


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

        # Store accessibility issues using handler
        if check_accessibility and results.get('accessibility'):
            AccessibilityIssueHandler.store_and_update(
                db, page_name, batch_id, results['accessibility']
            )

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
    Convert multiple DokuWiki pages to accessible documents (orchestrator wrapper).

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
        enable_discovery: Whether to auto-discover missing pages (defaults to True)
        max_discovery_depth: Max depth for page discovery (defaults to 2)

    Returns:
        Dictionary mapping page names to their conversion results
    """
    # Use ConversionOrchestrator for the full pipeline
    if output_dir is None:
        output_dir = "output"

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    db = None
    if use_database:
        db_path = output_path / "conversion_history.db"
        db = ConversionDatabase(str(db_path))

    orchestrator = ConversionOrchestrator(
        wiki_url=wiki_url,
        output_dir=output_dir,
        db=db,
        max_discovery_depth=max_discovery_depth
    )

    result = orchestrator.convert_pages(
        page_names=page_names,
        formats=formats,
        check_accessibility=check_accessibility,
        enable_discovery=enable_discovery,
        skip_recent=skip_recent
    )

    if db:
        db.close()

    return result['results']
