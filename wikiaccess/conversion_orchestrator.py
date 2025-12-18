#!/usr/bin/env python3
"""
Conversion Orchestrator - Separates concerns from unified.py

This module extracts the conversion logic from unified.py into a clean, testable
orchestrator that coordinates between the various subsystems:
- Markdown conversion
- Accessibility checking
- Report generation
- Link rewriting
- Discovery

This reduces unified.py from 752 lines to ~200 lines (framework code only).
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .scraper import DokuWikiHTTPClient
from .markdown_converter import MarkdownConverter
from .accessibility import AccessibilityChecker
from .reporting import ReportGenerator
from .accessibility_handler import AccessibilityIssueHandler
from .database import ConversionDatabase
from .link_rewriter import LinkRewriter
from .discovery import PageDiscoveryEngine
from .report_regenerator import ReportRegenerator
from .static_helper import copy_static_files


class ConversionOrchestrator:
    """Orchestrates the full conversion pipeline.

    This class coordinates between different subsystems to convert wiki pages
    to accessible HTML/DOCX with comprehensive reporting and discovery.

    Usage:
        >>> db = ConversionDatabase()
        >>> orchestrator = ConversionOrchestrator(
        ...     wiki_url='https://wiki.example.com',
        ...     output_dir='output',
        ...     db=db
        ... )
        >>> results = orchestrator.convert_pages(
        ...     page_names=['page1', 'page2'],
        ...     formats=['html', 'docx']
        ... )
    """

    def __init__(self, wiki_url: str, output_dir: str,
                 db: Optional[ConversionDatabase] = None,
                 max_discovery_depth: int = 2):
        """Initialize orchestrator.

        Args:
            wiki_url: Base wiki URL
            output_dir: Output directory path
            db: Optional database instance for persistence
            max_discovery_depth: Max depth for auto-discovery
        """
        self.wiki_url = wiki_url
        self.output_dir = Path(output_dir)
        self.db = db
        self.max_discovery_depth = max_discovery_depth

        # Initialize components
        client = DokuWikiHTTPClient(wiki_url)
        self.converter = MarkdownConverter(client, str(self.output_dir), include_accessibility_toolbar=True)
        self.accessibility_checker = AccessibilityChecker()
        self.report_regenerator = ReportRegenerator(str(self.output_dir))

    def convert_pages(self, page_names: List[str],
                      formats: List[str] = None,
                      check_accessibility: bool = True,
                      enable_discovery: bool = True,
                      skip_recent: bool = True,
                      batch_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert multiple pages with full pipeline.

        Args:
            page_names: List of page names to convert
            formats: Output formats ['html', 'docx']. Defaults to both.
            check_accessibility: Whether to check accessibility
            enable_discovery: Whether to auto-discover missing pages
            skip_recent: Whether to skip recently converted pages
            batch_id: Optional batch identifier. Auto-generated if not provided.

        Returns:
            Dict with conversion results and statistics
        """
        if formats is None:
            formats = ['html', 'docx']

        if batch_id is None:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize batch in database
        if self.db:
            self.db.start_batch(batch_id, self.wiki_url)

        results = {}
        statistics = {
            'total': len(page_names),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_images': 0,
            'failed_images': 0
        }

        print(f"\n{'='*70}")
        print(f"Converting {len(page_names)} Pages")
        print(f"Batch ID: {batch_id}")
        print(f"{'='*70}\n")

        # Convert each page
        for page_name in page_names:
            result = self._convert_single_page(
                page_name, formats, check_accessibility, batch_id, skip_recent
            )
            results[page_name] = result

            # Update statistics
            if result.get('skipped'):
                statistics['skipped'] += 1
            elif result.get('error'):
                statistics['failed'] += 1
            else:
                statistics['successful'] += 1
                statistics['total_images'] += result.get('image_count', 0)
                statistics['failed_images'] += result.get('failed_images', 0)

        # Generate reports if accessibility checking was enabled
        if check_accessibility:
            self._generate_reports(batch_id, results)

        # Run link rewriting
        link_stats = self._rewrite_links(batch_id, list(results.keys()))

        # Run discovery if enabled and links were broken
        if enable_discovery and link_stats['links_broken'] > 0:
            self._run_discovery(batch_id)

        # Complete batch
        if self.db:
            self.db.complete_batch(batch_id, statistics)

        # Regenerate comprehensive reports
        if check_accessibility:
            self._regenerate_comprehensive_reports()

        return {
            'batch_id': batch_id,
            'results': results,
            'statistics': statistics,
            'link_stats': link_stats
        }

    def _convert_single_page(self, page_name: str, formats: List[str],
                            check_accessibility: bool, batch_id: str,
                            skip_recent: bool) -> Dict[str, Any]:
        """Convert a single page.

        Args:
            page_name: Page name to convert
            formats: Output formats
            check_accessibility: Whether to check accessibility
            batch_id: Batch identifier
            skip_recent: Whether to skip if recently converted

        Returns:
            Conversion result dict
        """
        result = {'page_name': page_name}

        # Check if should skip
        if skip_recent and self.db and self.db.was_recently_converted(self.wiki_url, page_name):
            result['skipped'] = True
            return result

        try:
            # Convert page
            page_url = f"{self.wiki_url}/doku.php?id={page_name}"
            html_path, docx_path, stats = self.converter.convert_url(page_url)

            conversion_result = {
                'html': {'file_path': html_path, 'stats': stats} if html_path else None,
                'docx': {'file_path': docx_path, 'stats': stats} if docx_path else None,
                'image_count': stats.get('images', 0),
                'failed_images': stats.get('images_failed', 0)
            }

            result.update(conversion_result)

            # Check accessibility if requested
            if check_accessibility:
                accessibility_results = {}

                if html_path:
                    html_accessibility = self.accessibility_checker.check_html(html_path)
                    accessibility_results['html'] = html_accessibility

                if docx_path:
                    docx_accessibility = self.accessibility_checker.check_docx(docx_path)
                    accessibility_results['docx'] = docx_accessibility

                result['accessibility'] = accessibility_results

                # Store accessibility data
                if self.db:
                    AccessibilityIssueHandler.store_and_update(
                        self.db, page_name, batch_id, accessibility_results
                    )

            # Store in database
            if self.db:
                page_data = {
                    'wiki_url': self.wiki_url,
                    'page_id': page_name,
                    'batch_id': batch_id,
                    'conversion_status': 'SUCCESS',
                    'markdown_path': str(self.output_dir / 'markdown' / f"{page_name.replace(':', '_')}.md"),
                    'html_path': html_path,
                    'docx_path': docx_path,
                    'html_wcag_aa_score': result.get('accessibility', {}).get('html', {}).get('score_aa'),
                    'html_wcag_aaa_score': result.get('accessibility', {}).get('html', {}).get('score_aaa'),
                    'docx_wcag_aa_score': result.get('accessibility', {}).get('docx', {}).get('score_aa'),
                    'docx_wcag_aaa_score': result.get('accessibility', {}).get('docx', {}).get('score_aaa'),
                    'image_count': stats.get('images', 0),
                    'image_success_count': stats.get('images_success', 0),
                    'image_failed_count': stats.get('images_failed', 0),
                    'conversion_duration_seconds': 0,
                    'error_message': None
                }
                self.db.add_page_conversion(page_data)

                # Store image details
                for img in self.converter.image_details:
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
                        self.db.add_image(img_data)

            return result

        except Exception as e:
            result['error'] = str(e)
            return result

    def _generate_reports(self, batch_id: str, results: Dict[str, Any]) -> None:
        """Generate conversion reports for batch.

        Args:
            batch_id: Batch identifier
            results: Conversion results dict
        """
        print(f"\n{'='*70}\nGenerating Reports\n{'='*70}")

        # Build combined report from batch results
        page_reports = {}
        for page_name, result in results.items():
            if 'accessibility' in result:
                page_display_name = page_name.replace(':', '_')
                page_reports[page_display_name] = result['accessibility']

        if page_reports:
            reporter = ReportGenerator(str(self.output_dir / 'reports'))
            for page_name, accessibility in page_reports.items():
                reporter.add_page_reports(page_name, accessibility.get('html', {}),
                                        accessibility.get('docx', {}))
            reporter.generate_detailed_reports()

    def _rewrite_links(self, batch_id: str, page_names: List[str]) -> Dict[str, int]:
        """Rewrite internal links in converted pages.

        Args:
            batch_id: Batch identifier
            page_names: List of converted page names

        Returns:
            Link statistics dict
        """
        print(f"\n{'='*70}\nRewriting Links\n{'='*70}")

        link_rewriter = LinkRewriter(self.wiki_url, str(self.output_dir), self.db)
        link_stats = link_rewriter.rewrite_all_links(batch_id)

        if link_stats['links_broken'] > 0 and self.db:
            link_rewriter.generate_broken_links_report(batch_id, page_names)

        return link_stats

    def _run_discovery(self, batch_id: str) -> None:
        """Run auto-discovery on broken links.

        Args:
            batch_id: Batch identifier
        """
        if not self.db:
            return

        print(f"\n{'='*70}\nDiscovering New Pages\n{'='*70}")

        try:
            discovery_engine = PageDiscoveryEngine(
                self.db, self.wiki_url, self.max_discovery_depth
            )

            batch_info = self.db.get_batch_info(batch_id)
            current_depth = batch_info.get('discovery_depth', 0) if batch_info else 0

            if current_depth < self.max_discovery_depth:
                discovery_stats = discovery_engine.discover_from_batch(batch_id, current_depth)
                print(f"\nNew discoveries: {discovery_stats['new_discoveries']}")
                print(f"Already known: {discovery_stats['already_known']}")
                print(f"External links: {discovery_stats['external_links']}")

                if discovery_stats['new_discoveries'] > 0:
                    print(f"\n📋 Review with: python review_discoveries.py")

                discovery_engine.close()
            else:
                print(f"Reached max discovery depth ({self.max_discovery_depth})")

        except Exception as e:
            print(f"⚠️  Discovery error: {e}")

    def _regenerate_comprehensive_reports(self) -> None:
        """Regenerate comprehensive reports from all database data."""
        if not self.db:
            return

        print(f"\n{'='*70}\nRegenerating Comprehensive Reports\n{'='*70}")

        # Copy static CSS and JS files to reports directory
        copy_static_files(str(self.output_dir))

        self.report_regenerator.regenerate_all(self.db)

    def resolve_broken_links(self) -> int:
        """Resolve broken links that now point to converted pages.

        Returns:
            Number of links resolved
        """
        if not self.db:
            return 0

        print(f"\nResolving broken links that now point to converted pages...")
        resolved_count = self.db.resolve_converted_links()
        print(f"Resolved {resolved_count} links")

        return resolved_count
