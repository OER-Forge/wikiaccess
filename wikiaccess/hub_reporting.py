#!/usr/bin/env python3
"""
WikiAccess - Landing Hub Generator

Creates a unified landing page (index.html) that serves as the main entry point:
- Critical Issues section highlighting accessibility problems
- Statistics Dashboard with overall metrics
- Navigation Tiles to detailed reports
- Quick-fix suggestions with copy-to-clipboard functionality

Part of WikiAccess: Transform DokuWiki into Accessible Documents
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import html as html_lib
import json


class HubReportGenerator:
    """Generate unified landing hub with critical issues detection"""

    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_hub(self, page_reports: Dict, image_details: List[Dict]) -> str:
        """
        Generate landing hub (index.html) with critical issues and navigation

        Args:
            page_reports: Dict of {page_name: {'html': report, 'docx': report, 'html_stats': stats, 'docx_stats': stats}}
            image_details: List of image metadata dicts with alt_text_quality field

        Returns:
            Path to generated index.html
        """
        hub_path = self.reports_dir / 'index.html'

        # Detect critical issues
        critical_issues = self._detect_critical_issues(page_reports, image_details)

        # Calculate overall statistics
        stats = self._calculate_statistics(page_reports, image_details)

        # Build HTML
        html = self._build_hub_html(critical_issues, stats, page_reports)

        with open(hub_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n🏠 Landing Hub: {hub_path}")
        return str(hub_path)

    def _detect_critical_issues(self, page_reports: Dict, image_details: List[Dict]) -> Dict:
        """
        Detect critical accessibility issues

        Returns dict with:
            - missing_alt_text: list of images without alt-text
            - wcag_failures: list of pages with WCAG AA < 70%
            - broken_images: list of failed image downloads
            - multi_issue_pages: list of pages with 5+ issues
        """
        critical = {
            'missing_alt_text': [],
            'wcag_failures': [],
            'broken_images': [],
            'multi_issue_pages': []
        }

        # 1. Missing alt-text
        for img in image_details:
            if img.get('alt_text_quality') == 'missing':
                critical['missing_alt_text'].append({
                    'page': img['page_id'],
                    'filename': img.get('local_filename', 'unknown'),
                    'source_url': img.get('source_url', ''),
                    'suggested_alt': self._generate_suggested_alt_text(img)
                })

        # 2. WCAG AA failures (<70%)
        for page_name, reports in page_reports.items():
            html_report = reports.get('html', {})
            docx_report = reports.get('docx', {})

            html_aa = html_report.get('score_aa', 100)
            docx_aa = docx_report.get('score_aa', 100)

            if html_aa < 70 or docx_aa < 70:
                critical['wcag_failures'].append({
                    'page': page_name,
                    'html_score': html_aa,
                    'docx_score': docx_aa,
                    'html_issues': len(html_report.get('issues_aa', [])),
                    'docx_issues': len(docx_report.get('issues_aa', []))
                })

        # 3. Broken/failed images
        for img in image_details:
            if img.get('status') in ['failed', 'error']:
                critical['broken_images'].append({
                    'page': img['page_id'],
                    'filename': img.get('local_filename', 'unknown'),
                    'source_url': img.get('source_url', ''),
                    'error': img.get('error_message', 'Unknown error')
                })

        # 4. Pages with 5+ combined issues
        for page_name, reports in page_reports.items():
            html_report = reports.get('html', {})
            docx_report = reports.get('docx', {})

            total_issues = (
                len(html_report.get('issues_aa', [])) +
                len(html_report.get('issues_aaa', [])) +
                len(docx_report.get('issues_aa', [])) +
                len(docx_report.get('issues_aaa', []))
            )

            if total_issues >= 5:
                critical['multi_issue_pages'].append({
                    'page': page_name,
                    'total_issues': total_issues,
                    'html_aa_issues': len(html_report.get('issues_aa', [])),
                    'docx_aa_issues': len(docx_report.get('issues_aa', []))
                })

        return critical

    def _generate_suggested_alt_text(self, img: Dict) -> str:
        """Generate AI-suggested alt-text based on image context"""
        filename = img.get('local_filename', '')
        page_id = img.get('page_id', '')

        # Simple heuristic-based suggestions
        if filename:
            # Remove extension, replace underscores/hyphens with spaces, title case
            suggested = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ')
            suggested = suggested.title()

            # Add context from page if available
            if page_id:
                page_context = page_id.replace('_', ' ').replace(':', ' - ')
                return f"{suggested} (from {page_context})"

            return suggested

        return "Image description needed"

    def _calculate_statistics(self, page_reports: Dict, image_details: List[Dict]) -> Dict:
        """Calculate overall statistics for dashboard"""
        stats = {
            'total_pages': len(page_reports),
            'total_images': len(image_details),
            'avg_html_aa': 0,
            'avg_html_aaa': 0,
            'avg_docx_aa': 0,
            'avg_docx_aaa': 0,
            'total_aa_issues': 0,
            'images_success': 0,
            'images_failed': 0,
            'alt_text_missing': 0,
            'alt_text_manual': 0
        }

        if page_reports:
            stats['avg_html_aa'] = sum(r['html'].get('score_aa', 0) for r in page_reports.values()) / len(page_reports)
            stats['avg_html_aaa'] = sum(r['html'].get('score_aaa', 0) for r in page_reports.values()) / len(page_reports)
            stats['avg_docx_aa'] = sum(r['docx'].get('score_aa', 0) for r in page_reports.values()) / len(page_reports)
            stats['avg_docx_aaa'] = sum(r['docx'].get('score_aaa', 0) for r in page_reports.values()) / len(page_reports)
            stats['total_aa_issues'] = sum(
                len(r['html'].get('issues_aa', [])) + len(r['docx'].get('issues_aa', []))
                for r in page_reports.values()
            )

        if image_details:
            stats['images_success'] = len([img for img in image_details if img.get('status') in ['success', 'cached']])
            stats['images_failed'] = len([img for img in image_details if img.get('status') in ['failed', 'error']])
            stats['alt_text_missing'] = len([img for img in image_details if img.get('alt_text_quality') == 'missing'])
            stats['alt_text_manual'] = len([img for img in image_details if img.get('alt_text_quality') == 'manual'])

        return stats

    def _build_hub_html(self, critical_issues: Dict, stats: Dict, page_reports: Dict) -> str:
        """Build complete landing hub HTML"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build critical issues HTML
        critical_html = self._build_critical_issues_section(critical_issues)

        # Build statistics dashboard
        stats_html = self._build_statistics_section(stats)

        # Build navigation tiles
        nav_html = self._build_navigation_tiles(page_reports)

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiAccess - Accessibility Report Hub</title>
    {self._get_hub_css()}
</head>
<body>
    <header>
        <h1>♿ WikiAccess Report Hub</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        <p class="subtitle">Comprehensive accessibility analysis and reporting</p>
    </header>

    {critical_html}

    {stats_html}

    {nav_html}

    {self._get_hub_javascript()}
</body>
</html>'''

    def _build_critical_issues_section(self, critical: Dict) -> str:
        """Build critical issues section with quick-fix suggestions"""
        total_critical = (
            len(critical['missing_alt_text']) +
            len(critical['wcag_failures']) +
            len(critical['broken_images']) +
            len(critical['multi_issue_pages'])
        )

        if total_critical == 0:
            return '''
    <section class="critical-issues all-clear">
        <h2>🎉 Critical Issues</h2>
        <div class="all-clear-message">
            <p>✓ No critical issues detected! Your pages meet accessibility standards.</p>
        </div>
    </section>'''

        # Build issue cards
        issue_cards = []

        # 1. Missing alt-text
        if critical['missing_alt_text']:
            alt_text_items = []
            for item in critical['missing_alt_text'][:10]:  # Show first 10
                escaped_suggestion = html_lib.escape(item['suggested_alt'])
                alt_text_items.append(f'''
                    <div class="issue-item">
                        <div class="issue-details">
                            <strong>{html_lib.escape(item['filename'])}</strong>
                            <span class="issue-page">on {html_lib.escape(item['page'])}</span>
                        </div>
                        <div class="quick-fix">
                            <span class="suggestion">💡 {escaped_suggestion}</span>
                            <button class="copy-btn" onclick="copyToClipboard('{escaped_suggestion}')"
                                    title="Copy suggested alt-text">
                                📋 Copy
                            </button>
                        </div>
                    </div>''')

            more_text = f"<p class='more-items'>... and {len(critical['missing_alt_text']) - 10} more</p>" if len(critical['missing_alt_text']) > 10 else ""

            issue_cards.append(f'''
                <div class="issue-card issue-critical">
                    <h3>⚠️ Missing Alt-Text ({len(critical['missing_alt_text'])})</h3>
                    <div class="issue-list">
                        {"".join(alt_text_items)}
                    </div>
                    {more_text}
                    <a href="image_report.html" class="view-all-link">View Image Report →</a>
                </div>''')

        # 2. WCAG AA failures
        if critical['wcag_failures']:
            wcag_items = []
            for item in critical['wcag_failures'][:5]:
                wcag_items.append(f'''
                    <div class="issue-item">
                        <strong>{html_lib.escape(item['page'])}</strong>
                        <span class="score-display">
                            HTML: <span class="score-bad">{item['html_score']}%</span>
                            DOCX: <span class="score-bad">{item['docx_score']}%</span>
                        </span>
                        <a href="{item['page']}_accessibility.html" class="fix-link">Fix Issues →</a>
                    </div>''')

            more_text = f"<p class='more-items'>... and {len(critical['wcag_failures']) - 5} more</p>" if len(critical['wcag_failures']) > 5 else ""

            issue_cards.append(f'''
                <div class="issue-card issue-high">
                    <h3>📉 WCAG AA Failures ({len(critical['wcag_failures'])})</h3>
                    <p class="issue-description">Pages scoring below 70% on WCAG AA compliance</p>
                    <div class="issue-list">
                        {"".join(wcag_items)}
                    </div>
                    {more_text}
                </div>''')

        # 3. Broken images
        if critical['broken_images']:
            broken_items = []
            for item in critical['broken_images'][:5]:
                broken_items.append(f'''
                    <div class="issue-item">
                        <strong>{html_lib.escape(item['filename'])}</strong>
                        <span class="issue-page">on {html_lib.escape(item['page'])}</span>
                        <span class="error-detail">{html_lib.escape(item['error'][:50])}</span>
                    </div>''')

            more_text = f"<p class='more-items'>... and {len(critical['broken_images']) - 5} more</p>" if len(critical['broken_images']) > 5 else ""

            issue_cards.append(f'''
                <div class="issue-card issue-medium">
                    <h3>🖼️ Broken Images ({len(critical['broken_images'])})</h3>
                    <div class="issue-list">
                        {"".join(broken_items)}
                    </div>
                    {more_text}
                    <a href="image_report.html" class="view-all-link">View Image Report →</a>
                </div>''')

        # 4. Multi-issue pages
        if critical['multi_issue_pages']:
            multi_items = []
            for item in critical['multi_issue_pages'][:5]:
                multi_items.append(f'''
                    <div class="issue-item">
                        <strong>{html_lib.escape(item['page'])}</strong>
                        <span class="issue-count">{item['total_issues']} issues</span>
                        <a href="{item['page']}_accessibility.html" class="fix-link">Review →</a>
                    </div>''')

            more_text = f"<p class='more-items'>... and {len(critical['multi_issue_pages']) - 5} more</p>" if len(critical['multi_issue_pages']) > 5 else ""

            issue_cards.append(f'''
                <div class="issue-card issue-medium">
                    <h3>📄 Pages with Multiple Issues ({len(critical['multi_issue_pages'])})</h3>
                    <p class="issue-description">Pages with 5 or more accessibility issues</p>
                    <div class="issue-list">
                        {"".join(multi_items)}
                    </div>
                    {more_text}
                </div>''')

        return f'''
    <section class="critical-issues">
        <h2>🚨 Critical Issues ({total_critical})</h2>
        <p class="section-description">High-priority accessibility issues requiring immediate attention</p>
        <div class="issues-grid">
            {"".join(issue_cards)}
        </div>
    </section>'''

    def _build_statistics_section(self, stats: Dict) -> str:
        """Build statistics dashboard section"""
        def get_score_color(score):
            if score >= 90:
                return '#00cc66'
            elif score >= 70:
                return '#ffcc00'
            elif score >= 50:
                return '#ff8800'
            else:
                return '#cc0000'

        html_aa_color = get_score_color(stats['avg_html_aa'])
        html_aaa_color = get_score_color(stats['avg_html_aaa'])
        docx_aa_color = get_score_color(stats['avg_docx_aa'])
        docx_aaa_color = get_score_color(stats['avg_docx_aaa'])

        return f'''
    <section class="statistics-dashboard">
        <h2>📊 Overall Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_pages']}</div>
                <div class="stat-label">Pages Converted</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="background: {html_aa_color}; color: white; padding: 0.5rem; border-radius: 4px;">
                    {int(stats['avg_html_aa'])}%
                </div>
                <div class="stat-label">HTML WCAG AA</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="background: {html_aaa_color}; color: white; padding: 0.5rem; border-radius: 4px;">
                    {int(stats['avg_html_aaa'])}%
                </div>
                <div class="stat-label">HTML WCAG AAA</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="background: {docx_aa_color}; color: white; padding: 0.5rem; border-radius: 4px;">
                    {int(stats['avg_docx_aa'])}%
                </div>
                <div class="stat-label">DOCX WCAG AA</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="background: {docx_aaa_color}; color: white; padding: 0.5rem; border-radius: 4px;">
                    {int(stats['avg_docx_aaa'])}%
                </div>
                <div class="stat-label">DOCX WCAG AAA</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="color: #cc0000;">{stats['total_aa_issues']}</div>
                <div class="stat-label">Total AA Issues</div>
            </div>

            <div class="stat-card">
                <div class="stat-value">{stats['total_images']}</div>
                <div class="stat-label">Total Images</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="color: #28a745;">{stats['images_success']}</div>
                <div class="stat-label">Images Downloaded</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="color: #dc3545;">{stats['alt_text_missing']}</div>
                <div class="stat-label">Missing Alt-Text</div>
            </div>

            <div class="stat-card">
                <div class="stat-value" style="color: #28a745;">{stats['alt_text_manual']}</div>
                <div class="stat-label">Manual Alt-Text</div>
            </div>
        </div>
    </section>'''

    def _build_navigation_tiles(self, page_reports: Dict) -> str:
        """Build navigation tiles section"""
        return f'''
    <section class="navigation-tiles">
        <h2>📑 Detailed Reports</h2>
        <div class="tiles-grid">
            <a href="accessibility_report.html" class="nav-tile">
                <div class="tile-icon">♿</div>
                <h3>Accessibility Dashboard</h3>
                <p>WCAG compliance scores and issues for all pages</p>
            </a>

            <a href="image_report.html" class="nav-tile">
                <div class="tile-icon">📸</div>
                <h3>Image Report</h3>
                <p>Alt-text analysis, download status, and quality metrics</p>
            </a>

            <div class="nav-tile nav-tile-pages">
                <div class="tile-icon">📄</div>
                <h3>Individual Pages ({len(page_reports)})</h3>
                <ul class="page-list">
                    {"".join(f'<li><a href="{page}_accessibility.html">{page}</a></li>' for page in sorted(page_reports.keys())[:10])}
                    {f'<li><em>... and {len(page_reports) - 10} more pages</em></li>' if len(page_reports) > 10 else ''}
                </ul>
            </div>
        </div>
    </section>'''

    def _get_hub_css(self) -> str:
        """Return CSS styles for the hub"""
        return '''<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            color: #1a1a1a;
            background: #f5f5f5;
        }

        header {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }

        h1 {
            font-size: 2.5em;
            margin-bottom: 0.5rem;
        }

        h2 {
            font-size: 1.8em;
            margin-bottom: 1rem;
        }

        .timestamp {
            color: #666;
            font-size: 0.9em;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-top: 0.5rem;
        }

        section {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .section-description {
            color: #666;
            margin-bottom: 1.5rem;
        }

        /* Critical Issues Section */
        .critical-issues h2 {
            color: #dc3545;
        }

        .critical-issues.all-clear h2 {
            color: #28a745;
        }

        .all-clear-message {
            text-align: center;
            padding: 3rem;
            font-size: 1.2em;
            color: #28a745;
        }

        .issues-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
        }

        .issue-card {
            background: #f8f9fa;
            border-left: 4px solid;
            padding: 1.5rem;
            border-radius: 4px;
        }

        .issue-card.issue-critical {
            border-color: #dc3545;
        }

        .issue-card.issue-high {
            border-color: #ff8800;
        }

        .issue-card.issue-medium {
            border-color: #ffc107;
        }

        .issue-card h3 {
            margin-bottom: 0.5rem;
            font-size: 1.2em;
        }

        .issue-description {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 1rem;
        }

        .issue-list {
            margin: 1rem 0;
        }

        .issue-item {
            padding: 0.75rem;
            background: white;
            border-radius: 4px;
            margin-bottom: 0.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .issue-details {
            display: flex;
            flex-direction: column;
        }

        .issue-page {
            font-size: 0.85em;
            color: #666;
        }

        .quick-fix {
            display: flex;
            align-items: center;
            gap: 1rem;
            background: #e7f3ff;
            padding: 0.5rem;
            border-radius: 4px;
        }

        .suggestion {
            flex: 1;
            font-size: 0.9em;
            color: #0066cc;
        }

        .copy-btn {
            padding: 0.25rem 0.75rem;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            white-space: nowrap;
        }

        .copy-btn:hover {
            background: #0052a3;
        }

        .copy-btn.copied {
            background: #28a745;
        }

        .score-display {
            font-size: 0.9em;
        }

        .score-bad {
            color: #dc3545;
            font-weight: 600;
        }

        .issue-count {
            background: #ffc107;
            color: #333;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .fix-link, .view-all-link {
            color: #0066cc;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9em;
        }

        .fix-link:hover, .view-all-link:hover {
            text-decoration: underline;
        }

        .more-items {
            margin-top: 1rem;
            font-style: italic;
            color: #666;
            font-size: 0.9em;
        }

        .error-detail {
            font-size: 0.85em;
            color: #999;
            font-style: italic;
        }

        /* Statistics Dashboard */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }

        .stat-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #e0e0e0;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            line-height: 1;
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-top: 0.5rem;
        }

        /* Navigation Tiles */
        .tiles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .nav-tile {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            text-decoration: none;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            display: block;
        }

        .nav-tile:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }

        .nav-tile:nth-child(1) {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .nav-tile:nth-child(2) {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .nav-tile:nth-child(3) {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        .nav-tile-pages {
            color: #1a1a1a;
            background: #f8f9fa !important;
            border: 2px solid #e0e0e0;
        }

        .tile-icon {
            font-size: 3em;
            margin-bottom: 0.5rem;
        }

        .nav-tile h3 {
            font-size: 1.3em;
            margin-bottom: 0.5rem;
            color: inherit;
        }

        .nav-tile p {
            font-size: 0.95em;
            opacity: 0.9;
        }

        .page-list {
            list-style: none;
            margin-top: 1rem;
            max-height: 200px;
            overflow-y: auto;
        }

        .page-list li {
            padding: 0.25rem 0;
        }

        .page-list a {
            color: #0066cc;
            text-decoration: none;
        }

        .page-list a:hover {
            text-decoration: underline;
        }

        /* Responsive */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }

            .issues-grid {
                grid-template-columns: 1fr;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .tiles-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>'''

    def _get_hub_javascript(self) -> str:
        """Return JavaScript for copy-to-clipboard functionality"""
        return '''<script>
        // Copy suggested alt-text to clipboard
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                // Find the button that was clicked
                const button = event.target;
                const originalText = button.textContent;

                // Show feedback
                button.textContent = '✓ Copied!';
                button.classList.add('copied');

                // Reset after 2 seconds
                setTimeout(() => {
                    button.textContent = originalText;
                    button.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy:', err);
                alert('Failed to copy to clipboard');
            });
        }
    </script>'''


if __name__ == '__main__':
    # Test with sample data
    print("Hub report generator module loaded successfully")
