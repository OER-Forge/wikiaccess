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


class ImageReportGenerator:
    """Generate comprehensive image download reports"""

    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / 'images'

    def generate_image_report(self, image_details: List[Dict]) -> str:
        """
        Generate comprehensive image report with sortable tables

        Args:
            image_details: List of image metadata dictionaries

        Returns:
            Path to generated report
        """
        report_path = self.reports_dir / 'image_report.html'

        html = self._build_image_report_html(image_details)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n📸 Image Report: {report_path}")
        return str(report_path)

    def _build_image_report_html(self, image_details: List[Dict]) -> str:
        """Build the complete image report HTML"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Calculate statistics
        total_images = len(image_details)
        successful = len([img for img in image_details if img['status'] in ['success', 'cached']])
        failed = len([img for img in image_details if img['status'] in ['failed', 'error']])
        skipped = len([img for img in image_details if img['status'] == 'skipped'])

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
            by_type, by_page, total_size_mb
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
    {self._get_css_styles()}
</head>
<body>
    <header>
        <h1>📸 Image Download Report</h1>
        <p class="timestamp">Generated: {timestamp}</p>
    </header>

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

            <label for="filter-page">Filter by Page:</label>
            <select id="filter-page" onchange="filterTable()" aria-label="Filter images by page">
                <option value="all">All Pages</option>
                {"".join(f'<option value="{page}">{page}</option>' for page in sorted(by_page.keys()))}
            </select>
        </div>

        {table_html}
    </section>

    {self._get_javascript()}
</body>
</html>'''
        return html

    def _build_statistics_dashboard(self, total, success, failed, skipped,
                                    by_type, by_page, total_size_mb) -> str:
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

    def _build_sortable_table(self, image_details: List[Dict]) -> str:
        """Build sortable HTML table with image details"""
        rows = []
        for idx, img in enumerate(image_details):
            status_class = f"status-{img['status']}"
            thumbnail = self._get_thumbnail_html(img)
            file_size_str = self._format_file_size(img['file_size'])

            error_display = f'<span class="error-msg" title="{img["error_message"]}">{img["error_message"][:50]}...</span>' if img['error_message'] else ''

            rows.append(f'''
                <tr class="image-row" data-status="{img['status']}" data-page="{img['page_id']}">
                    <td>{idx + 1}</td>
                    <td class="thumbnail-cell">{thumbnail}</td>
                    <td class="page-cell">{img['page_id']}</td>
                    <td class="type-cell">{img['type']}</td>
                    <td class="filename-cell" title="{img['local_filename'] or 'N/A'}">{img['local_filename'] or 'N/A'}</td>
                    <td class="status-cell"><span class="{status_class}">{img['status'].upper()}</span></td>
                    <td class="size-cell" data-size="{img['file_size'] or 0}">{file_size_str}</td>
                    <td class="dimensions-cell">{img['dimensions'] or 'N/A'}</td>
                    <td class="timestamp-cell">{img['timestamp'][:19]}</td>
                    <td class="error-cell">{error_display}</td>
                </tr>''')

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
                        <th onclick="sortTable(6)" role="button" tabindex="0">Size ▲▼</th>
                        <th onclick="sortTable(7)" role="button" tabindex="0">Dimensions ▲▼</th>
                        <th onclick="sortTable(8)" role="button" tabindex="0">Timestamp ▲▼</th>
                        <th>Error</th>
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
            max-width: 1600px;
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
            min-width: 1200px;
        }

        thead {
            background: #0047b3;
            color: white;
            position: sticky;
            top: 0;
        }

        th {
            padding: 1rem;
            text-align: left;
            cursor: pointer;
            user-select: none;
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
            padding: 0.75rem 1rem;
        }

        /* Thumbnail */
        .thumbnail-cell {
            text-align: center;
        }

        .thumbnail {
            width: 80px;
            height: 80px;
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
            width: 80px;
            height: 80px;
            line-height: 80px;
            text-align: center;
            background: #f0f0f0;
            border-radius: 4px;
            color: #999;
            font-size: 2rem;
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

        /* Error messages */
        .error-msg {
            color: #dc3545;
            font-size: 0.85em;
            font-style: italic;
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
        }
    </style>'''

    def _get_javascript(self) -> str:
        """Return JavaScript for sorting and filtering"""
        return '''<script>
        // Sort table by column
        let sortDirection = 1;
        let lastSortedColumn = -1;

        function sortTable(columnIndex) {
            const table = document.getElementById('image-table');
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);

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

                // Special handling for size column (use data attribute)
                if (columnIndex === 6) {
                    aValue = parseInt(a.cells[columnIndex].dataset.size) || 0;
                    bValue = parseInt(b.cells[columnIndex].dataset.size) || 0;
                    return sortDirection * (aValue - bValue);
                }

                // String comparison
                return sortDirection * aValue.localeCompare(bValue);
            });

            // Re-append rows in new order
            rows.forEach(row => tbody.appendChild(row));
        }

        // Filter table
        function filterTable() {
            const statusFilter = document.getElementById('filter-status').value;
            const pageFilter = document.getElementById('filter-page').value;
            const rows = document.querySelectorAll('.image-row');

            rows.forEach(row => {
                const status = row.dataset.status;
                const page = row.dataset.page;

                const statusMatch = statusFilter === 'all' || status === statusFilter;
                const pageMatch = pageFilter === 'all' || page === pageFilter;

                row.style.display = (statusMatch && pageMatch) ? '' : 'none';
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
