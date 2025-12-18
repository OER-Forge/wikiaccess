#!/usr/bin/env python3
"""
Comprehensive Report Regeneration Facade

This module consolidates all report regeneration logic that was scattered across:
- regenerate_accessibility_report.py
- regenerate_image_report.py
- regenerate_broken_links_report.py
- inline code in unified.py

Previously these patterns were duplicated 4+ times. Now it's a single facade.
"""

from pathlib import Path
from typing import Optional
from .database import ConversionDatabase
from .reporting import ReportGenerator
from .image_reporting import ImageReportGenerator
from .hub_reporting import HubReportGenerator
from .report_components import get_breadcrumb_navigation, build_report_header, build_stat_cards
from .static_helper import get_css_links
from .template_renderer import TemplateRenderer


class ReportRegenerator:
    """Facade for regenerating comprehensive reports from database."""

    def __init__(self, output_dir: str):
        """Initialize regenerator.

        Args:
            output_dir: Root output directory
        """
        self.output_dir = Path(output_dir)
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def regenerate_accessibility_report(self, db: ConversionDatabase) -> Optional[str]:
        """Regenerate comprehensive accessibility report with all pages from database.

        Args:
            db: ConversionDatabase instance

        Returns:
            Path to generated report, or None if error
        """
        try:
            all_pages = db.get_all_pages_with_scores()

            if not all_pages:
                return None

            print(f"📋 Regenerating accessibility report ({len(all_pages)} pages)...")

            reporter = ReportGenerator(str(self.reports_dir))

            for page_data in all_pages:
                page_id = page_data['page_id']
                page_display_name = page_id.replace(':', '_')

                html_report = {
                    'score_aa': page_data['html_wcag_aa_score'] or 0,
                    'score_aaa': page_data['html_wcag_aaa_score'] or 0,
                    'issues_aa': [],
                    'issues_aaa': [],
                    'warnings': []
                }
                docx_report = {
                    'score_aa': page_data['docx_wcag_aa_score'] or 0,
                    'score_aaa': page_data['docx_wcag_aaa_score'] or 0,
                    'issues_aa': [],
                    'issues_aaa': [],
                    'warnings': []
                }

                reporter.add_page_reports(page_display_name, html_report, docx_report)

            reporter.generate_detailed_reports()
            report_path = self.reports_dir / 'accessibility_report.html'

            print(f"✓ Accessibility report: {report_path}")
            return str(report_path)

        except Exception as e:
            print(f"✗ Error regenerating accessibility report: {e}")
            return None

    def regenerate_image_report(self, db: ConversionDatabase) -> Optional[str]:
        """Regenerate comprehensive image report with all images from database.

        Args:
            db: ConversionDatabase instance

        Returns:
            Path to generated report, or None if error
        """
        try:
            all_images = db.get_all_images_for_report()

            if not all_images:
                return None

            print(f"📸 Regenerating image report ({len(all_images)} images)...")

            # Convert database rows to image_details format
            image_details = []
            for img_data in all_images:
                local_filename = img_data['local_filename']
                local_path = str(self.output_dir / 'images' / local_filename) if local_filename else None

                img_dict = {
                    'page_id': img_data['page_id'],
                    'type': img_data['type'],
                    'source_url': img_data['source_url'],
                    'local_filename': local_filename,
                    'local_path': local_path,
                    'status': img_data['status'],
                    'file_size': img_data['file_size'],
                    'dimensions': img_data['dimensions'],
                    'alt_text': img_data['alt_text'],
                    'error_message': img_data['error_message'],
                    'downloaded_at': img_data['downloaded_at']
                }
                image_details.append(img_dict)

            reporter = ImageReportGenerator(str(self.output_dir))
            report_path = reporter.generate_image_report(image_details)

            print(f"✓ Image report: {report_path}")
            return report_path

        except Exception as e:
            print(f"✗ Error regenerating image report: {e}")
            return None

    def regenerate_landing_hub(self, db: ConversionDatabase,
                               image_details: Optional[list] = None,
                               link_stats: Optional[dict] = None) -> Optional[str]:
        """Regenerate comprehensive landing hub with all pages from database.

        Args:
            db: ConversionDatabase instance
            image_details: Optional image details for hub
            link_stats: Optional link statistics for hub

        Returns:
            Path to generated report, or None if error
        """
        try:
            all_pages = db.get_all_pages_with_scores()

            if not all_pages:
                return None

            print(f"🏠 Regenerating landing hub ({len(all_pages)} pages)...")

            # Build page_reports dict
            page_reports = {}
            for page_data in all_pages:
                page_id = page_data['page_id']
                page_display_name = page_id.replace(':', '_')

                page_reports[page_display_name] = {
                    'html': {
                        'score_aa': page_data['html_wcag_aa_score'] or 0,
                        'score_aaa': page_data['html_wcag_aaa_score'] or 0,
                    },
                    'docx': {
                        'score_aa': page_data['docx_wcag_aa_score'] or 0,
                        'score_aaa': page_data['docx_wcag_aaa_score'] or 0,
                    }
                }

            hub_generator = HubReportGenerator(str(self.output_dir))
            report_path = hub_generator.generate_hub(
                page_reports,
                image_details or [],
                link_stats or {}
            )

            print(f"✓ Landing hub: {report_path}")
            return str(report_path)

        except Exception as e:
            print(f"✗ Error regenerating landing hub: {e}")
            return None

    def regenerate_broken_links_report(self, db: ConversionDatabase) -> Optional[str]:
        """Regenerate comprehensive broken links report using Jinja2 templates.

        Args:
            db: ConversionDatabase instance

        Returns:
            Path to generated report, or None if error
        """
        try:
            all_broken = db.get_all_broken_links()
            page_names_list = db.get_pages_with_broken_links()

            if not all_broken or not page_names_list:
                return None

            print(f"🔗 Regenerating broken links report ({len(all_broken)} links)...")

            # Build report components
            nav_html = get_breadcrumb_navigation('broken_links', page_list=page_names_list, show_broken_links=True)
            header_html = build_report_header(
                title="🔗 Broken Links Report",
                subtitle="Internal wiki links pointing to pages that haven't been converted",
                breadcrumb=[
                    {'label': '🏠 Home', 'url': 'index.html'},
                    {'label': 'Broken Links'}
                ]
            )

            stats_html = build_stat_cards([
                {'value': len(all_broken), 'label': 'Broken Links', 'color': '#dc3545'},
                {'value': sum(link['reference_count'] for link in all_broken), 'label': 'Total References', 'color': '#ff8800'}
            ], grid_size='narrow')

            css_links = get_css_links()

            # Use template renderer
            template_renderer = TemplateRenderer(str(self.output_dir))
            html_content = template_renderer.render_broken_links_report(
                links=all_broken,
                css_links=css_links,
                navigation=nav_html,
                header=header_html,
                stats=stats_html
            )

            # Write report
            report_path = self.reports_dir / 'broken_links_report.html'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✓ Broken links report: {report_path}")
            return str(report_path)

        except Exception as e:
            print(f"✗ Error regenerating broken links report: {e}")
            return None

    def regenerate_all(self, db: ConversionDatabase,
                      image_details: Optional[list] = None,
                      link_stats: Optional[dict] = None) -> dict:
        """Regenerate all reports at once.

        Args:
            db: ConversionDatabase instance
            image_details: Optional image details
            link_stats: Optional link statistics

        Returns:
            Dict with report paths and status
        """
        print(f"\n{'='*70}\nRegenerating All Reports\n{'='*70}\n")

        # Gather image details if not provided
        if not image_details:
            all_images = db.get_all_images_for_report()
            if all_images:
                image_details = []
                for img_data in all_images:
                    local_filename = img_data['local_filename']
                    local_path = str(self.output_dir / 'images' / local_filename) if local_filename else None
                    image_details.append({
                        'page_id': img_data['page_id'],
                        'type': img_data['type'],
                        'source_url': img_data['source_url'],
                        'local_filename': local_filename,
                        'local_path': local_path,
                        'status': img_data['status'],
                        'file_size': img_data['file_size'],
                        'dimensions': img_data['dimensions'],
                        'alt_text': img_data['alt_text'],
                        'error_message': img_data['error_message'],
                        'downloaded_at': img_data['downloaded_at']
                    })

        results = {
            'accessibility': self.regenerate_accessibility_report(db),
            'image': self.regenerate_image_report(db),
            'hub': self.regenerate_landing_hub(db, image_details, link_stats),
            'broken_links': self.regenerate_broken_links_report(db),
        }

        print(f"\n{'='*70}")
        print(f"Report Regeneration Complete")
        print(f"{'='*70}\n")

        return results
