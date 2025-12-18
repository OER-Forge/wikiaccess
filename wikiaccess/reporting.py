#!/usr/bin/env python3
"""
WikiAccess - Accessibility Report Generator

Creates HTML dashboard and detailed reports for accessibility checks:
- WCAG AA/AAA compliance scores
- Media conversion statistics (images/videos/equations)
- Side-by-side HTML vs DOCX comparison
- Issue detection and recommendations
- Clickable links to converted files

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import html as html_lib
import os
from markupsafe import Markup
from .report_components import (
    get_breadcrumb_navigation, get_breadcrumb_javascript,
    build_report_header, build_stat_cards, build_action_buttons
)
from .static_helper import get_css_links
from .template_renderer import TemplateRenderer


class ReportGenerator:
    """Generate accessibility compliance reports"""

    def __init__(self, output_dir: str = 'output', db=None):
        self.output_dir = Path(output_dir)
        self.page_reports = {}  # page_name -> {html_report, docx_report}
        self.db = db  # Database connection for enhanced reporting
        self.template_renderer = TemplateRenderer(str(self.output_dir))
    
    def add_page_reports(self, page_name: str, html_report: Dict, docx_report: Dict,
                        html_stats: Dict = None, docx_stats: Dict = None):
        """Add reports for both HTML and DOCX versions of a page"""
        self.page_reports[page_name] = {
            'html': html_report,
            'docx': docx_report,
            'page_name': page_name,
            'html_stats': html_stats or {},
            'docx_stats': docx_stats or {}
        }
    
    def generate_dashboard(self) -> str:
        """Generate main dashboard HTML"""
        dashboard_path = self.output_dir / 'accessibility_report.html'
        
        html = self._build_dashboard_html()
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n📊 Accessibility Dashboard: {dashboard_path}")
        return str(dashboard_path)
    
    def generate_detailed_reports(self):
        """Generate detailed reports for all pages"""
        for page_name, reports in self.page_reports.items():
            report_path = self.output_dir / f'{page_name}_accessibility.html'
            
            html = self._build_combined_detail_html(
                page_name, 
                reports['html'], 
                reports['docx'],
                reports.get('html_stats'),
                reports.get('docx_stats')
            )
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  ✓ Detailed report: {report_path}")
    
    def _build_dashboard_html(self) -> str:
        """Build dashboard HTML using template renderer"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build breadcrumb navigation
        page_list = list(self.page_reports.keys())
        broken_links_exists = (self.output_dir / 'broken_links_report.html').exists()
        nav_html = get_breadcrumb_navigation('accessibility', page_list=page_list, show_broken_links=broken_links_exists)

        # Calculate overall stats
        total_pages = len(self.page_reports)

        if total_pages == 0:
            avg_html_aa = avg_html_aaa = avg_docx_aa = avg_docx_aaa = 0
            total_html_issues_aa = total_html_issues_aaa = 0
            total_docx_issues_aa = total_docx_issues_aaa = 0
        else:
            avg_html_aa = sum(r['html']['score_aa'] for r in self.page_reports.values()) / total_pages
            avg_html_aaa = sum(r['html']['score_aaa'] for r in self.page_reports.values()) / total_pages
            avg_docx_aa = sum(r['docx']['score_aa'] for r in self.page_reports.values()) / total_pages
            avg_docx_aaa = sum(r['docx']['score_aaa'] for r in self.page_reports.values()) / total_pages
            total_html_issues_aa = sum(len(r['html']['issues_aa']) for r in self.page_reports.values())
            total_html_issues_aaa = sum(len(r['html']['issues_aaa']) for r in self.page_reports.values())
            total_docx_issues_aa = sum(len(r['docx']['issues_aa']) for r in self.page_reports.values())
            total_docx_issues_aaa = sum(len(r['docx']['issues_aaa']) for r in self.page_reports.values())

        # Build header with breadcrumb
        header_html = build_report_header(
            title="✓ Accessibility Compliance Dashboard",
            subtitle="WCAG 2.1 compliance analysis for all converted pages",
            timestamp=timestamp,
            breadcrumb=[
                {'label': '🏠 Home', 'url': 'index.html'},
                {'label': 'Accessibility'}
            ]
        )

        # Build stat cards
        stats_html = build_stat_cards([
            {'value': total_pages, 'label': 'Pages Converted'},
            {'value': f'{int(avg_html_aa)}%', 'label': 'HTML WCAG AA', 'color': self._get_score_color(avg_html_aa)},
            {'value': f'{int(avg_html_aaa)}%', 'label': 'HTML WCAG AAA', 'color': self._get_score_color(avg_html_aaa)},
            {'value': f'{int(avg_docx_aa)}%', 'label': 'DOCX WCAG AA', 'color': self._get_score_color(avg_docx_aa)},
            {'value': f'{int(avg_docx_aaa)}%', 'label': 'DOCX WCAG AAA', 'color': self._get_score_color(avg_docx_aaa)},
            {'value': total_html_issues_aa + total_docx_issues_aa, 'label': 'Total AA Issues', 'color': '#dc3545'}
        ])

        # Build page data for template
        pages = []
        for page_name, reports in self.page_reports.items():
            html_report = reports['html']
            docx_report = reports['docx']

            pages.append({
                'name': page_name,
                'detail_link': f'{page_name}_accessibility.html',
                'html_file_link': f'../html/{page_name}.html',
                'docx_file_link': f'../docx/{page_name}.docx',
                'html_aa_badge': Markup(self._get_score_badge(html_report['score_aa'])),
                'html_aaa_badge': Markup(self._get_score_badge(html_report['score_aaa'])),
                'html_aa_issues': len(html_report['issues_aa']),
                'docx_aa_badge': Markup(self._get_score_badge(docx_report['score_aa'])),
                'docx_aaa_badge': Markup(self._get_score_badge(docx_report['score_aaa'])),
                'docx_aa_issues': len(docx_report['issues_aa'])
            })

        # Use template renderer
        return self.template_renderer.render_accessibility_dashboard(
            pages=pages,
            css_links=get_css_links(),
            navigation=nav_html,
            header=header_html,
            stats=stats_html,
            breadcrumb_javascript=get_breadcrumb_javascript()
        )

    def _get_score_badge(self, score: int) -> str:
        """Generate HTML badge for score"""
        badge_class = 'success' if score >= 90 else 'warning' if score >= 70 else 'danger'
        return f'<span class="report-badge score {badge_class}">{score}%</span>'

    def _get_enhanced_data(self, page_name):
        """Get enhanced data if database available"""
        if not self.db:
            return {}, {}, [], []
        
        try:
            # Get metadata
            cursor = self.db.conn.execute(
                'SELECT converted_at, html_wcag_aa_score FROM pages WHERE page_id = ? ORDER BY converted_at DESC LIMIT 1',
                (page_name.replace('_', ':'),))
            meta = cursor.fetchone()
            metadata = {'converted_at': meta[0] if meta else 'N/A', 'score': meta[1] if meta else 0}
            
            # Get links  
            cursor = self.db.conn.execute(
                'SELECT target_page_id, resolution_status FROM links WHERE source_page_id = ? LIMIT 20',
                (page_name.replace('_', ':'),))
            links = {'outgoing': [{'target': r[0], 'status': r[1]} for r in cursor.fetchall()]}
            
            # Get images
            cursor = self.db.conn.execute(
                'SELECT local_filename, status, alt_text_quality FROM images WHERE page_id = ? LIMIT 20',
                (page_name.replace('_', ':'),))
            images = [{'name': r[0], 'status': r[1], 'quality': r[2]} for r in cursor.fetchall()]
            
            # Get history
            cursor = self.db.conn.execute(
                'SELECT converted_at, html_wcag_aa_score FROM pages WHERE page_id = ? ORDER BY converted_at DESC LIMIT 5',
                (page_name.replace('_', ':'),))
            history = [{'date': r[0], 'score': r[1]} for r in cursor.fetchall()]
            
            return metadata, links, images, history
        except:
            return {}, {}, [], []

    def _build_combined_detail_html(self, page_name: str, html_report: Dict, docx_report: Dict,
                                    html_stats: Optional[Dict] = None, docx_stats: Optional[Dict] = None) -> str:
        """Build combined detailed report HTML using Jinja2 template"""

        # Build breadcrumb navigation
        page_list = list(self.page_reports.keys())
        broken_links_exists = (self.output_dir / 'broken_links_report.html').exists()
        nav_html = get_breadcrumb_navigation('page_detail', current_page_name=page_name, page_list=page_list, show_broken_links=broken_links_exists)

        # Build header with breadcrumb
        header_html = build_report_header(
            title=html_lib.escape(page_name),
            subtitle="Detailed accessibility compliance analysis",
            breadcrumb=[
                {'label': '🏠 Home', 'url': 'index.html'},
                {'label': 'Accessibility', 'url': 'accessibility_report.html'},
                {'label': page_name}
            ]
        )

        # Build action buttons
        actions = [
            {'label': 'View HTML', 'url': f'../html/{page_name}.html', 'icon': '📄', 'text': 'View HTML', 'target': '_blank'},
            {'label': 'Download DOCX', 'url': f'../docx/{page_name}.docx', 'icon': '📝', 'text': 'Download DOCX', 'download': True},
            {'label': 'View Markdown', 'url': f'../markdown/{page_name}.md', 'icon': '📊', 'text': 'View Markdown', 'target': '_blank'}
        ]

        # Prepare CSS links
        css_links = get_css_links()

        # Use template renderer
        return self.template_renderer.render_page_report(
            page_name=page_name,
            html_report=html_report,
            docx_report=docx_report,
            css_links=css_links,
            navigation=nav_html,
            breadcrumb='',  # Included in header
            header=header_html,
            actions=actions
        )
    
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 90:
            return '#00cc66'  # Green
        elif score >= 70:
            return '#ffcc00'  # Yellow
        elif score >= 50:
            return '#ff8800'  # Orange
        else:
            return '#cc0000'  # Red
