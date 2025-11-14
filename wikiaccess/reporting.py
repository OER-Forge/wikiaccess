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


class ReportGenerator:
    """Generate accessibility compliance reports"""
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.page_reports = {}  # page_name -> {html_report, docx_report}
    
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
        """Build dashboard HTML"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate overall stats
        total_pages = len(self.page_reports)
        
        if total_pages == 0:
            avg_html_aa = avg_html_aaa = avg_docx_aa = avg_docx_aaa = 0
            total_html_issues_aa = total_html_issues_aaa = 0
            total_docx_issues_aa = total_docx_issues_aaa = 0
        else:
            # Average scores for HTML and DOCX
            avg_html_aa = sum(r['html']['score_aa'] for r in self.page_reports.values()) / total_pages
            avg_html_aaa = sum(r['html']['score_aaa'] for r in self.page_reports.values()) / total_pages
            avg_docx_aa = sum(r['docx']['score_aa'] for r in self.page_reports.values()) / total_pages
            avg_docx_aaa = sum(r['docx']['score_aaa'] for r in self.page_reports.values()) / total_pages
            
            # Total issues
            total_html_issues_aa = sum(len(r['html']['issues_aa']) for r in self.page_reports.values())
            total_html_issues_aaa = sum(len(r['html']['issues_aaa']) for r in self.page_reports.values())
            total_docx_issues_aa = sum(len(r['docx']['issues_aa']) for r in self.page_reports.values())
            total_docx_issues_aaa = sum(len(r['docx']['issues_aaa']) for r in self.page_reports.values())
        
        # Build page table rows
        page_rows = []
        for page_name, reports in self.page_reports.items():
            html_report = reports['html']
            docx_report = reports['docx']
            
            # HTML scores
            html_aa = html_report['score_aa']
            html_aaa = html_report['score_aaa']
            html_aa_color = self._get_score_color(html_aa)
            html_aaa_color = self._get_score_color(html_aaa)
            
            # DOCX scores
            docx_aa = docx_report['score_aa']
            docx_aaa = docx_report['score_aaa']
            docx_aa_color = self._get_score_color(docx_aa)
            docx_aaa_color = self._get_score_color(docx_aaa)
            
            detail_link = f'{page_name}_accessibility.html'
            html_file_link = f'html/{page_name}.html'
            docx_file_link = f'docx/{page_name}.docx'
            
            page_rows.append(f'''
                <tr>
                    <td>
                        <a href="{detail_link}">{html_lib.escape(page_name)}</a>
                        <div style="font-size: 0.8em; color: #666; margin-top: 0.25rem;">
                            <a href="{html_file_link}" target="_blank">📄 HTML</a> | 
                            <a href="{docx_file_link}" target="_blank">📄 DOCX</a>
                        </div>
                    </td>
                    <td style="background: {html_aa_color}; font-weight: bold;">{html_aa}%</td>
                    <td style="background: {html_aaa_color}; font-weight: bold;">{html_aaa}%</td>
                    <td>{len(html_report['issues_aa'])}</td>
                    <td style="background: {docx_aa_color}; font-weight: bold;">{docx_aa}%</td>
                    <td style="background: {docx_aaa_color}; font-weight: bold;">{docx_aaa}%</td>
                    <td>{len(docx_report['issues_aa'])}</td>
                </tr>
            ''')
        
        overall_html_aa_color = self._get_score_color(avg_html_aa)
        overall_html_aaa_color = self._get_score_color(avg_html_aaa)
        overall_docx_aa_color = self._get_score_color(avg_docx_aa)
        overall_docx_aaa_color = self._get_score_color(avg_docx_aaa)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Compliance Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            color: #1a1a1a;
            background: #f5f5f5;
        }}
        
        header {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2em;
            margin-bottom: 0.5rem;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            line-height: 1;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 0.5rem;
        }}
        
        table {{
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-collapse: collapse;
        }}
        
        thead {{
            background: #0066cc;
            color: white;
        }}
        
        th, td {{
            padding: 1rem;
            text-align: center;
        }}
        
        th:first-child, td:first-child {{
            text-align: left;
        }}
        
        tbody tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        tbody tr:hover {{
            background: #f0f0f0;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .section-header {{
            background: #e6f2ff;
            font-weight: bold;
            text-align: center;
        }}
    </style>
</head>
<body>
    <header>
        <h1>♿ Accessibility Compliance Dashboard</h1>
        <p class="timestamp">Generated: {timestamp}</p>
    </header>
    
    <div class="summary">
        <div class="stat-card">
            <div class="stat-value">{total_pages}</div>
            <div class="stat-label">Pages Converted</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" style="background: {overall_html_aa_color}; padding: 0.5rem; border-radius: 4px;">{int(avg_html_aa)}%</div>
            <div class="stat-label">HTML WCAG AA</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" style="background: {overall_html_aaa_color}; padding: 0.5rem; border-radius: 4px;">{int(avg_html_aaa)}%</div>
            <div class="stat-label">HTML WCAG AAA</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" style="background: {overall_docx_aa_color}; padding: 0.5rem; border-radius: 4px;">{int(avg_docx_aa)}%</div>
            <div class="stat-label">DOCX WCAG AA</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" style="background: {overall_docx_aaa_color}; padding: 0.5rem; border-radius: 4px;">{int(avg_docx_aaa)}%</div>
            <div class="stat-label">DOCX WCAG AAA</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" style="color: #cc0000;">{total_html_issues_aa + total_docx_issues_aa}</div>
            <div class="stat-label">Total AA Issues</div>
        </div>
    </div>
    
    <h2 style="margin-bottom: 1rem;">Page Reports</h2>
    
    <table>
        <thead>
            <tr>
                <th rowspan="2">Page Name</th>
                <th colspan="3" class="section-header">HTML</th>
                <th colspan="3" class="section-header">DOCX</th>
            </tr>
            <tr>
                <th>WCAG AA</th>
                <th>WCAG AAA</th>
                <th>AA Issues</th>
                <th>WCAG AA</th>
                <th>WCAG AAA</th>
                <th>AA Issues</th>
            </tr>
        </thead>
        <tbody>
            {''.join(page_rows)}
        </tbody>
    </table>
    
    <footer>
        <p>WCAG 2.1 Accessibility Compliance Report | <a href="https://www.w3.org/WAI/WCAG21/quickref/">WCAG Quick Reference</a></p>
    </footer>
</body>
</html>'''
    
    def _build_combined_detail_html(self, page_name: str, html_report: Dict, docx_report: Dict, 
                                    html_stats: Optional[Dict] = None, docx_stats: Optional[Dict] = None) -> str:
        """Build combined detailed report HTML for both HTML and DOCX"""
        
        html_stats = html_stats or {}
        docx_stats = docx_stats or {}
        
        # HTML scores
        html_aa = html_report['score_aa']
        html_aaa = html_report['score_aaa']
        html_aa_color = self._get_score_color(html_aa)
        html_aaa_color = self._get_score_color(html_aaa)
        
        # DOCX scores
        docx_aa = docx_report['score_aa']
        docx_aaa = docx_report['score_aaa']
        docx_aa_color = self._get_score_color(docx_aa)
        docx_aaa_color = self._get_score_color(docx_aaa)
        
        # Build issue lists for HTML
        html_issues_aa_html = self._build_issue_list(html_report['issues_aa'], 'error')
        html_issues_aaa_html = self._build_issue_list(html_report['issues_aaa'], 'error-aaa')
        html_warnings_html = self._build_issue_list(html_report['warnings'], 'warning')
        
        # Build issue lists for DOCX
        docx_issues_aa_html = self._build_issue_list(docx_report['issues_aa'], 'error')
        docx_issues_aaa_html = self._build_issue_list(docx_report['issues_aaa'], 'error-aaa')
        docx_warnings_html = self._build_issue_list(docx_report['warnings'], 'warning')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report: {html_lib.escape(page_name)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            color: #1a1a1a;
            background: #f5f5f5;
        }}
        
        header {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2em;
            margin-bottom: 1rem;
        }}
        
        .format-sections {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }}
        
        .format-section {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .format-section h2 {{
            font-size: 1.5em;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .scores {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .score {{
            flex: 1;
            text-align: center;
        }}
        
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            padding: 0.5rem;
            border-radius: 8px;
        }}
        
        .score-label {{
            font-size: 0.8em;
            color: #666;
            margin-top: 0.5rem;
        }}
        
        .issue-section {{
            margin-top: 1.5rem;
        }}
        
        .issue-section h3 {{
            font-size: 1.1em;
            margin-bottom: 0.5rem;
        }}
        
        .issue-list {{
            list-style: none;
            font-size: 0.9em;
        }}
        
        .issue-list li {{
            padding: 0.3rem 0;
        }}
        
        .error {{ color: #cc0000; }}
        .error-aaa {{ color: #9900cc; }}
        .warning {{ color: #ff8800; }}
        .success {{ color: #00aa00; }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 1rem;
            color: #0066cc;
            text-decoration: none;
        }}
        
        .back-link:hover {{
            text-decoration: underline;
        }}
        
        .file-links {{
            background: #e6f2ff;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
        }}
        
        .file-links a {{
            display: inline-block;
            margin: 0 1rem;
            padding: 0.5rem 1rem;
            background: white;
            border-radius: 4px;
            text-decoration: none;
            color: #0066cc;
            font-weight: bold;
        }}
        
        .file-links a:hover {{
            background: #f0f0f0;
        }}
    </style>
</head>
<body>
    <a href="accessibility_report.html" class="back-link">← Back to Dashboard</a>
    
    <div class="file-links">
        <a href="html/{page_name}.html" target="_blank">📄 View HTML Version</a>
        <a href="docx/{page_name}.docx" target="_blank">📄 Download DOCX Version</a>
    </div>
    
    <header>
        <h1>{html_lib.escape(page_name)}</h1>
    </header>
    
    <div class="format-sections">
        <!-- HTML Report -->
        <div class="format-section">
            <h2>HTML Version</h2>
            <div class="scores">
                <div class="score">
                    <div class="score-value" style="background: {html_aa_color};">{html_aa}%</div>
                    <div class="score-label">WCAG AA</div>
                </div>
                <div class="score">
                    <div class="score-value" style="background: {html_aaa_color};">{html_aaa}%</div>
                    <div class="score-label">WCAG AAA</div>
                </div>
            </div>
            
            {self._build_media_stats("HTML", html_stats)}
            
            {self._build_format_issues("AA Issues", html_issues_aa_html, html_report['issues_aa'])}
            {self._build_format_issues("AAA Issues", html_issues_aaa_html, html_report['issues_aaa'])}
            {self._build_format_issues("Warnings", html_warnings_html, html_report['warnings'])}
        </div>
        
        <!-- DOCX Report -->
        <div class="format-section">
            <h2>DOCX Version</h2>
            <div class="scores">
                <div class="score">
                    <div class="score-value" style="background: {docx_aa_color};">{docx_aa}%</div>
                    <div class="score-label">WCAG AA</div>
                </div>
                <div class="score">
                    <div class="score-value" style="background: {docx_aaa_color};">{docx_aaa}%</div>
                    <div class="score-label">WCAG AAA</div>
                </div>
            </div>
            
            {self._build_media_stats("DOCX", docx_stats)}
            
            {self._build_format_issues("AA Issues", docx_issues_aa_html, docx_report['issues_aa'])}
            {self._build_format_issues("AAA Issues", docx_issues_aaa_html, docx_report['issues_aaa'])}
            {self._build_format_issues("Warnings", docx_warnings_html, docx_report['warnings'])}
        </div>
    </div>
</body>
</html>'''
    
    def _build_format_issues(self, title: str, content: str, issues: list) -> str:
        """Build issues section for a format"""
        if not issues:
            return ''
        return f'''
            <div class="issue-section">
                <h3>{title}</h3>
                {content}
            </div>'''
    
    def _build_media_stats(self, format_name: str, stats: Dict) -> str:
        """Build media statistics display"""
        if not stats:
            return ''
        
        images_success = stats.get('images_success', 0)
        images_failed = stats.get('images_failed', 0)
        videos_success = stats.get('videos_success', 0)
        videos_failed = stats.get('videos_failed', 0)
        equations = stats.get('equations', 0)
        
        total_images = images_success + images_failed
        total_videos = videos_success + videos_failed
        
        if total_images == 0 and total_videos == 0 and equations == 0:
            return ''
        
        stats_html = '<div style="background: #f5f5f5; padding: 1rem; margin: 1rem 0; border-radius: 4px;">'
        stats_html += '<h4 style="margin: 0 0 0.5rem 0;">Conversion Statistics</h4>'
        stats_html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.5rem;">'
        
        if total_images > 0:
            img_color = '#28a745' if images_failed == 0 else '#ffc107' if images_success > 0 else '#dc3545'
            stats_html += f'''
                <div style="padding: 0.5rem; background: white; border-radius: 4px;">
                    <div style="font-size: 0.9rem; color: #666;">Images</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: {img_color};">
                        {images_success}/{total_images}
                    </div>
                    <div style="font-size: 0.8rem; color: #999;">embedded</div>
                </div>'''
        
        if total_videos > 0:
            vid_color = '#28a745' if videos_failed == 0 else '#ffc107' if videos_success > 0 else '#dc3545'
            stats_html += f'''
                <div style="padding: 0.5rem; background: white; border-radius: 4px;">
                    <div style="font-size: 0.9rem; color: #666;">Videos</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: {vid_color};">
                        {videos_success}/{total_videos}
                    </div>
                    <div style="font-size: 0.8rem; color: #999;">embedded</div>
                </div>'''
        
        if equations > 0:
            stats_html += f'''
                <div style="padding: 0.5rem; background: white; border-radius: 4px;">
                    <div style="font-size: 0.9rem; color: #666;">Equations</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #28a745;">
                        {equations}
                    </div>
                    <div style="font-size: 0.8rem; color: #999;">converted</div>
                </div>'''
        
        stats_html += '</div></div>'
        return stats_html
    
    def _build_section(self, title: str, content: str) -> str:
        """Build a report section"""
        return f'''
    <div class="section">
        <h2>{title}</h2>
        {content}
    </div>'''
    
    def _build_issue_list(self, items: List[str], css_class: str) -> str:
        """Build HTML list of issues"""
        if not items:
            return '<p>None</p>'
        
        list_items = '\n'.join(f'<li class="{css_class}">{html_lib.escape(item)}</li>' for item in items)
        return f'<ul class="issue-list">\n{list_items}\n</ul>'
    
    def _build_recommendations(self, report: Dict) -> str:
        """Generate recommendations based on issues"""
        recommendations = []
        
        if report['issues_aa']:
            recommendations.append('<li>Fix all WCAG AA issues to meet minimum accessibility standards</li>')
        
        if any('alt' in issue.lower() for issue in report['issues_aa']):
            recommendations.append('<li>Add descriptive alt text to all images</li>')
        
        if any('heading' in issue.lower() for issue in report['issues_aa']):
            recommendations.append('<li>Ensure proper heading hierarchy (H1 → H2 → H3, etc.)</li>')
        
        if any('link' in issue.lower() for issue in report['issues_aa']):
            recommendations.append('<li>Use descriptive link text (avoid "click here")</li>')
        
        if any('contrast' in warning.lower() for warning in report['warnings']):
            recommendations.append('<li>Test color contrast ratio (minimum 4.5:1 for normal text)</li>')
        
        if any('lang' in issue.lower() for issue in report['issues_aa']):
            recommendations.append('<li>Set document language attribute for screen readers</li>')
        
        if not recommendations:
            recommendations.append('<li>✓ No major issues found - document meets WCAG guidelines</li>')
        
        recommendations.append('<li>Test with screen readers (NVDA, JAWS, VoiceOver)</li>')
        recommendations.append('<li>Verify keyboard navigation works properly</li>')
        
        return '\n'.join(recommendations)
    
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
