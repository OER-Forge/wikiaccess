#!/usr/bin/env python3
"""
WikiAccess - Image Report Generator

Creates comprehensive, sortable HTML reports for image downloads:
- Thumbnail previews with lightbox
- Sortable tables (by page, status, size, date, type)
- Detailed metadata (dimensions, file size, timestamps)
- Error messages and statistics
- WCAG AAA accessible design

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import base64
import html as html_lib
from .report_components import (
    get_breadcrumb_navigation, get_breadcrumb_javascript,
    build_report_header, build_stat_cards
)
from .static_helper import get_css_links


class ImageReportGenerator:
    """Generate comprehensive image download reports"""

    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / 'images'

    def generate_image_report(self, image_details: List[Dict], page_list: List[str] = None) -> str:
        """
        Generate comprehensive image report with sortable tables

        Args:
            image_details: List of image metadata dictionaries
            page_list: Optional list of page names for navigation sidebar

        Returns:
            Path to generated report
        """
        report_path = self.reports_dir / 'image_report.html'

        html = self._build_image_report_html(image_details, page_list or [])

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n📸 Image Report: {report_path}")
        return str(report_path)

    def _classify_alt_text(self, img: Dict) -> str:
        """
        Classify alt-text quality for an image
        Returns: 'missing', 'auto-generated', or 'manual'
        """
        alt_text = img.get('alt_text', '')
        filename = img.get('local_filename', '')

        if not alt_text or alt_text.strip() == '':
            return 'missing'

        # Check if alt-text is auto-generated from filename
        # Auto-generated alt-text is typically: filename without extension, with underscores/hyphens replaced by spaces
        if filename:
            # Generate what the auto-generated alt-text would be
            auto_generated = filename.replace('_', ' ').replace('-', ' ').rsplit('.', 1)[0]
            if alt_text.strip().lower() == auto_generated.strip().lower():
                return 'auto-generated'

        # Otherwise, it's manually provided
        return 'manual'

    def _build_image_report_html(self, image_details: List[Dict], page_list: List[str]) -> str:
        """Build the complete image report HTML using component system"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build breadcrumb navigation
        broken_links_exists = (self.reports_dir / 'broken_links_report.html').exists()
        nav_html = get_breadcrumb_navigation('images', page_list=page_list, show_broken_links=broken_links_exists)

        # Build header with breadcrumb
        header_html = build_report_header(
            title="📸 Image Download Report",
            subtitle="Comprehensive analysis of image downloads and alt-text quality",
            timestamp=timestamp,
            breadcrumb=[
                {'label': '🏠 Home', 'url': 'index.html'},
                {'label': 'Images'}
            ]
        )

        # Calculate statistics
        total_images = len(image_details)
        successful = len([img for img in image_details if img['status'] in ['success', 'cached']])
        failed = len([img for img in image_details if img['status'] in ['failed', 'error']])
        skipped = len([img for img in image_details if img['status'] == 'skipped'])

        # Classify alt-text quality for all images
        for img in image_details:
            img['alt_text_quality'] = self._classify_alt_text(img)

        # Count alt-text quality
        alt_text_stats = {
            'missing': len([img for img in image_details if img['alt_text_quality'] == 'missing']),
            'auto_generated': len([img for img in image_details if img['alt_text_quality'] == 'auto-generated']),
            'manual': len([img for img in image_details if img['alt_text_quality'] == 'manual'])
        }

        # Group by type
        by_type = {}
        for img in image_details:
            img_type = img['type']
            by_type[img_type] = by_type.get(img_type, 0) + 1

        # Group by page
        by_page = {}
        for img in image_details:
            page_id = img['page_id']
            by_page[page_id] = by_page.get(page_id, 0) + 1

        # Calculate total file size
        total_size = sum(img['file_size'] or 0 for img in image_details)
        total_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0

        # Build statistics dashboard
        stats_html = self._build_statistics_dashboard(
            total_images, successful, failed, skipped,
            by_type, by_page, total_size_mb, alt_text_stats
        )

        # Build sortable table
        table_html = self._build_sortable_table(image_details)

        # Complete HTML page
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Download Report - WikiAccess</title>
{get_css_links()}
</head>
<body>
    {nav_html}

    <div class="report-container">
        {header_html}

        {stats_html}

        <section class="table-section">
            <h2>Detailed Image Table</h2>
            <div class="table-controls">
                <label for="filter-status">Filter by Status:</label>
                <select id="filter-status" onchange="filterTable()" aria-label="Filter images by status">
                    <option value="all">All</option>
                    <option value="success">Success</option>
                    <option value="cached">Cached</option>
                    <option value="failed">Failed</option>
                    <option value="error">Error</option>
                    <option value="skipped">Skipped</option>
                </select>

                <label for="filter-alt-quality">Filter by Alt-Text:</label>
                <select id="filter-alt-quality" onchange="filterTable()" aria-label="Filter images by alt-text quality">
                    <option value="all">All</option>
                    <option value="missing">⚠️ Missing</option>
                    <option value="auto-generated">🤖 Auto-generated</option>
                    <option value="manual">✓ Manual</option>
                </select>

                <label for="filter-page">Filter by Page:</label>
                <select id="filter-page" onchange="filterTable()" aria-label="Filter images by page">
                    <option value="all">All Pages</option>
                    {"".join(f'<option value="{page}">{page}</option>' for page in sorted(by_page.keys()))}
                </select>
            </div>

            {table_html}
        </section>
    </div>

    {get_breadcrumb_javascript()}
    {self._get_javascript()}
</body>
</html>'''
        return html

    def _build_statistics_dashboard(self, total, success, failed, skipped,
                                    by_type, by_page, total_size_mb, alt_text_stats) -> str:
        """Build statistics dashboard HTML"""
        success_rate = int((success / total * 100)) if total > 0 else 0

        return f'''
    <section class="statistics">
        <h2>Summary Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Images</div>
            </div>

            <div class="stat-card stat-success">
                <div class="stat-value">{success}</div>
                <div class="stat-label">Downloaded</div>
            </div>

            <div class="stat-card stat-failed">
                <div class="stat-value">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>

            <div class="stat-card stat-skipped">
                <div class="stat-value">{skipped}</div>
                <div class="stat-label">Skipped</div>
            </div>

            <div class="stat-card">
                <div class="stat-value">{success_rate}%</div>
                <div class="stat-label">Success Rate</div>
            </div>

            <div class="stat-card">
                <div class="stat-value">{total_size_mb:.2f} MB</div>
                <div class="stat-label">Total Size</div>
            </div>
        </div>

        <div class="breakdown">
            <div class="breakdown-section">
                <h3>Alt-Text Quality</h3>
                <ul>
                    <li class="alt-missing"><strong>Missing:</strong> {alt_text_stats['missing']} ⚠️</li>
                    <li class="alt-auto"><strong>Auto-generated:</strong> {alt_text_stats['auto_generated']}</li>
                    <li class="alt-manual"><strong>Manual:</strong> {alt_text_stats['manual']} ✓</li>
                </ul>
            </div>

            <div class="breakdown-section">
                <h3>By Type</h3>
                <ul>
                    {"".join(f'<li><strong>{img_type}:</strong> {count}</li>' for img_type, count in sorted(by_type.items()))}
                </ul>
            </div>

            <div class="breakdown-section">
                <h3>By Page</h3>
                <ul class="page-list">
                    {"".join(f'<li><strong>{page}:</strong> {count} images</li>' for page, count in sorted(by_page.items())[:10])}
                    {f'<li><em>... and {len(by_page) - 10} more pages</em></li>' if len(by_page) > 10 else ''}
                </ul>
            </div>
        </div>
    </section>'''

    def _get_alt_text_badge(self, quality: str, alt_text: str) -> str:
        """Generate HTML badge for alt-text quality"""
        if quality == 'missing':
            return '<span class="alt-badge alt-badge-missing" title="No alt-text provided">⚠️ Missing</span>'
        elif quality == 'auto-generated':
            return f'<span class="alt-badge alt-badge-auto" title="Auto-generated from filename: {alt_text}">🤖 Auto</span>'
        else:  # manual
            return f'<span class="alt-badge alt-badge-manual" title="Manual alt-text: {alt_text}">✓ Manual</span>'

    def _build_sortable_table(self, image_details: List[Dict]) -> str:
        """Build sortable HTML table with image details and expandable rows"""
        rows = []
        for idx, img in enumerate(image_details):
            status_class = f"status-{img['status']}"
            thumbnail = self._get_thumbnail_html(img)
            file_size_str = self._format_file_size(img['file_size'])
            alt_text_badge = self._get_alt_text_badge(img['alt_text_quality'], img.get('alt_text', ''))

            # Truncate alt-text for display (show first 40 chars)
            alt_text_full = img.get('alt_text', 'N/A')
            alt_text_display = alt_text_full[:40] + '...' if len(alt_text_full) > 40 else alt_text_full

            error_display = f'<span class="error-msg" title="{img["error_message"]}">{img["error_message"][:50]}...</span>' if img['error_message'] else ''

            # Build expandable details section
            details_html = f'''
                <tr class="detail-row" id="detail-{idx}" style="display: none;">
                    <td colspan="9">
                        <div class="detail-content">
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <strong>Full Alt-Text:</strong>
                                    <p>{html_lib.escape(alt_text_full)}</p>
                                </div>
                                <div class="detail-item">
                                    <strong>Source URL:</strong>
                                    <p>{html_lib.escape(img.get('source_url', 'N/A'))}</p>
                                </div>
                                <div class="detail-item">
                                    <strong>Dimensions:</strong>
                                    <p>{img.get('dimensions', 'N/A')}</p>
                                </div>
                                <div class="detail-item">
                                    <strong>Timestamp:</strong>
                                    <p>{img.get('timestamp', 'N/A')[:19]}</p>
                                </div>
                                {f'''<div class="detail-item full-width">
                                    <strong>Error Details:</strong>
                                    <p class="error-detail">{html_lib.escape(img["error_message"])}</p>
                                </div>''' if img.get('error_message') else ''}
                            </div>
                        </div>
                    </td>
                </tr>'''

            rows.append(f'''
                <tr class="image-row" data-status="{img['status']}" data-page="{img['page_id']}" data-alt-quality="{img['alt_text_quality']}"
                    onclick="toggleDetails({idx})" style="cursor: pointer;" title="Click to expand details">
                    <td>{idx + 1}</td>
                    <td class="thumbnail-cell">{thumbnail}</td>
                    <td class="page-cell">{img['page_id']}</td>
                    <td class="type-cell">{img['type']}</td>
                    <td class="filename-cell" title="{img['local_filename'] or 'N/A'}">{img['local_filename'] or 'N/A'}</td>
                    <td class="status-cell"><span class="{status_class}">{img['status'].upper()}</span></td>
                    <td class="alt-quality-cell">{alt_text_badge}</td>
                    <td class="alt-text-cell" title="{html_lib.escape(alt_text_full)}">{html_lib.escape(alt_text_display)}</td>
                    <td class="size-cell" data-size="{img['file_size'] or 0}">{file_size_str}</td>
                </tr>
                {details_html}''')

        return f'''
        <div class="table-wrapper">
            <table id="image-table" class="sortable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)" role="button" tabindex="0">#</th>
                        <th>Thumbnail</th>
                        <th onclick="sortTable(2)" role="button" tabindex="0">Page ▲▼</th>
                        <th onclick="sortTable(3)" role="button" tabindex="0">Type ▲▼</th>
                        <th onclick="sortTable(4)" role="button" tabindex="0">Filename ▲▼</th>
                        <th onclick="sortTable(5)" role="button" tabindex="0">Status ▲▼</th>
                        <th onclick="sortTable(6)" role="button" tabindex="0">Quality ▲▼</th>
                        <th onclick="sortTable(7)" role="button" tabindex="0">Alt-Text ▲▼</th>
                        <th onclick="sortTable(8)" role="button" tabindex="0">Size ▲▼</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>'''

    def _get_thumbnail_html(self, img: Dict) -> str:
        """Generate thumbnail HTML for image"""
        if img['status'] in ['success', 'cached'] and img['local_path']:
            local_path = Path(img['local_path'])
            if local_path.exists():
                # Use relative path from reports dir to images dir
                rel_path = f"../images/{img['local_filename']}"
                return f'<a href="{rel_path}" class="thumbnail-link" target="_blank"><img src="{rel_path}" alt="{img["alt_text"]}" class="thumbnail" loading="lazy"></a>'

        # No thumbnail available
        return '<span class="no-thumbnail">✗</span>'

    def _format_file_size(self, size_bytes) -> str:
        """Format file size in human-readable format"""
        if size_bytes is None:
            return 'N/A'

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} TB"

    def _get_css_styles(self) -> str:
        """Return CSS styles for the report"""
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
            color: #1a1a1a;
            background: #f5f5f5;
        }

        .main-content {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }

        header {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 2em;
            margin-bottom: 0.5rem;
        }

        h2 {
            font-size: 1.5em;
            margin-bottom: 1rem;
        }

        .timestamp {
            color: #666;
            font-size: 0.9em;
        }

        /* Statistics Dashboard */
        .statistics {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 6px;
            text-align: center;
            border: 2px solid #e0e0e0;
        }

        .stat-card.stat-success {
            border-color: #28a745;
            background: #e8f5e9;
        }

        .stat-card.stat-failed {
            border-color: #dc3545;
            background: #ffebee;
        }

        .stat-card.stat-skipped {
            border-color: #ffc107;
            background: #fff9e6;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            line-height: 1;
            color: #1a1a1a;
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-top: 0.5rem;
        }

        .breakdown {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }

        .breakdown-section h3 {
            font-size: 1.1em;
            margin-bottom: 0.75rem;
            color: #333;
        }

        .breakdown-section ul {
            list-style: none;
        }

        .breakdown-section li {
            padding: 0.25rem 0;
            border-bottom: 1px solid #e0e0e0;
        }

        /* Table Section */
        .table-section {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .table-controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }

        .table-controls label {
            font-weight: 600;
        }

        .table-controls select {
            padding: 0.5rem;
            border: 2px solid #0047b3;
            border-radius: 4px;
            font-size: 0.9rem;
            min-width: 150px;
        }

        .table-wrapper {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 900px;
        }

        thead {
            background: #0047b3;
            color: white;
            position: sticky;
            top: 0;
        }

        th {
            padding: 0.75rem;
            text-align: left;
            cursor: pointer;
            user-select: none;
            font-size: 0.9em;
        }

        th:hover {
            background: #003580;
        }

        tbody tr {
            border-bottom: 1px solid #e0e0e0;
        }

        tbody tr:nth-child(even) {
            background: #f9f9f9;
        }

        tbody tr:hover {
            background: #f0f0f0;
        }

        td {
            padding: 0.5rem 0.75rem;
            font-size: 0.9em;
        }

        /* Cell-specific styling */
        .thumbnail-cell {
            text-align: center;
            padding: 0.5rem;
        }

        .page-cell {
            max-width: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .filename-cell {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: monospace;
            font-size: 0.85em;
        }

        .alt-text-cell {
            max-width: 180px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .type-cell {
            text-transform: uppercase;
            font-size: 0.8em;
            font-weight: 600;
            color: #666;
        }

        .size-cell {
            text-align: right;
            font-variant-numeric: tabular-nums;
            font-family: monospace;
            font-size: 0.85em;
        }

        .thumbnail {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 4px;
            border: 2px solid #e0e0e0;
        }

        .thumbnail-link:hover .thumbnail {
            border-color: #0047b3;
            transform: scale(1.05);
            transition: all 0.2s ease;
        }

        .no-thumbnail {
            display: inline-block;
            width: 60px;
            height: 60px;
            line-height: 60px;
            text-align: center;
            background: #f0f0f0;
            border-radius: 4px;
            color: #999;
            font-size: 1.5rem;
        }

        /* Status badges */
        .status-success, .status-cached {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85em;
        }

        .status-cached {
            background: #17a2b8;
        }

        .status-failed, .status-error {
            background: #dc3545;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85em;
        }

        .status-skipped {
            background: #ffc107;
            color: #333;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85em;
        }

        /* Alt-text quality badges */
        .alt-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85em;
            white-space: nowrap;
        }

        .alt-badge-missing {
            background: #dc3545;
            color: white;
        }

        .alt-badge-auto {
            background: #ffc107;
            color: #333;
        }

        .alt-badge-manual {
            background: #28a745;
            color: white;
        }

        /* Alt-text quality in breakdown section */
        .alt-missing {
            color: #dc3545;
            font-weight: 600;
        }

        .alt-auto {
            color: #cc8800;
        }

        .alt-manual {
            color: #28a745;
            font-weight: 600;
        }

        /* Error messages */
        .error-msg {
            color: #dc3545;
            font-size: 0.85em;
            font-style: italic;
        }

        /* Expandable detail rows */
        .image-row:hover {
            background: #e3f2fd !important;
        }

        .detail-row {
            background: #f8f9fa !important;
        }

        .detail-content {
            padding: 1.5rem;
            animation: slideDown 0.3s ease;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .detail-item {
            background: white;
            padding: 1rem;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }

        .detail-item.full-width {
            grid-column: 1 / -1;
        }

        .detail-item strong {
            display: block;
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            letter-spacing: 0.05em;
        }

        .detail-item p {
            margin: 0;
            color: #1a1a1a;
            word-break: break-word;
        }

        .error-detail {
            color: #dc3545;
            font-family: monospace;
            font-size: 0.9em;
        }

        /* Responsive */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .breakdown {
                grid-template-columns: 1fr;
            }

            .thumbnail {
                width: 50px;
                height: 50px;
            }

            .no-thumbnail {
                width: 50px;
                height: 50px;
                line-height: 50px;
                font-size: 1.2rem;
            }

            th, td {
                padding: 0.5rem;
                font-size: 0.85em;
            }
        }
    </style>'''

    def _get_javascript(self) -> str:
        """Return JavaScript for sorting, filtering, and expandable rows"""
        return '''<script>
        // Toggle expandable detail rows
        function toggleDetails(rowIndex) {
            const detailRow = document.getElementById('detail-' + rowIndex);
            if (detailRow.style.display === 'none' || detailRow.style.display === '') {
                detailRow.style.display = 'table-row';
            } else {
                detailRow.style.display = 'none';
            }
        }

        // Sort table by column
        let sortDirection = 1;
        let lastSortedColumn = -1;

        function sortTable(columnIndex) {
            const table = document.getElementById('image-table');
            const tbody = table.tBodies[0];

            // Get only image rows (not detail rows)
            const rows = Array.from(tbody.rows).filter(row => row.classList.contains('image-row'));

            // Toggle direction if same column
            if (columnIndex === lastSortedColumn) {
                sortDirection *= -1;
            } else {
                sortDirection = 1;
                lastSortedColumn = columnIndex;
            }

            rows.sort((a, b) => {
                let aValue = a.cells[columnIndex].textContent.trim();
                let bValue = b.cells[columnIndex].textContent.trim();

                // Special handling for size column (use data attribute) - column index 8
                if (columnIndex === 8) {
                    aValue = parseInt(a.cells[columnIndex].dataset.size) || 0;
                    bValue = parseInt(b.cells[columnIndex].dataset.size) || 0;
                    return sortDirection * (aValue - bValue);
                }

                // String comparison
                return sortDirection * aValue.localeCompare(bValue);
            });

            // Clear tbody and re-append rows with their detail rows
            tbody.innerHTML = '';
            rows.forEach((row, idx) => {
                tbody.appendChild(row);
                // Find and append corresponding detail row
                const detailRow = document.getElementById('detail-' + row.getAttribute('onclick').match(/\\d+/)[0]);
                if (detailRow) {
                    tbody.appendChild(detailRow);
                }
            });
        }

        // Filter table
        function filterTable() {
            const statusFilter = document.getElementById('filter-status').value;
            const pageFilter = document.getElementById('filter-page').value;
            const altQualityFilter = document.getElementById('filter-alt-quality').value;
            const rows = document.querySelectorAll('.image-row');

            rows.forEach(row => {
                const status = row.dataset.status;
                const page = row.dataset.page;
                const altQuality = row.dataset.altQuality;

                const statusMatch = statusFilter === 'all' || status === statusFilter;
                const pageMatch = pageFilter === 'all' || page === pageFilter;
                const altQualityMatch = altQualityFilter === 'all' || altQuality === altQualityFilter;

                row.style.display = (statusMatch && pageMatch && altQualityMatch) ? '' : 'none';
            });
        }

        // Keyboard accessibility for sortable headers
        document.querySelectorAll('th[onclick]').forEach(th => {
            th.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    th.click();
                }
            });
        });
    </script>'''


if __name__ == '__main__':
    # Test with sample data
    sample_data = [
        {
            'page_id': 'test_page',
            'type': 'wiki_image',
            'source_url': 'test.png',
            'local_filename': 'test.png',
            'local_path': '/path/to/test.png',
            'timestamp': datetime.now().isoformat(),
            'alt_text': 'Test image',
            'status': 'success',
            'error_message': None,
            'file_size': 12345,
            'dimensions': '800x600'
        }
    ]

    generator = ImageReportGenerator()
    generator.generate_image_report(sample_data)
    print("✓ Test report generated")
