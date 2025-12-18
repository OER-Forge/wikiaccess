#!/usr/bin/env python3
"""
WikiAccess - Shared Report Components

Reusable UI components for reports including navigation sidebar,
search functionality, and common styling.
"""

from typing import List, Dict, Optional
from .static_helper import get_css_links


def get_navigation_sidebar(current_page: str, page_list: Optional[List[str]] = None, show_broken_links: bool = False) -> str:
    """
    Generate persistent navigation sidebar for all reports

    Args:
        current_page: Current page identifier ('hub', 'accessibility', 'images', 'broken_links', 'page_detail')
        page_list: Optional list of page names for the pages section
        show_broken_links: Whether to show the broken links navigation item

    Returns:
        HTML string for navigation sidebar
    """
    page_list = page_list or []

    # Determine active state
    hub_active = "active" if current_page == "hub" else ""
    accessibility_active = "active" if current_page == "accessibility" else ""
    images_active = "active" if current_page == "images" else ""
    broken_links_active = "active" if current_page == "broken_links" else ""
    pages_active = "active" if current_page == "page_detail" else ""

    # Build page list HTML
    page_items_html = ""
    if page_list:
        page_items = []
        for page in sorted(page_list)[:20]:  # Show first 20
            page_items.append(f'<li><a href="{page}_accessibility.html">{page}</a></li>')
        if len(page_list) > 20:
            page_items.append(f'<li class="more-pages"><em>... and {len(page_list) - 20} more pages</em></li>')
        page_items_html = '\n'.join(page_items)

    return f'''
    <nav class="report-sidebar" id="report-sidebar" aria-label="Report navigation">
        <div class="sidebar-header">
            <h2>📊 WikiAccess</h2>
            <button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Toggle sidebar">
                <span class="toggle-icon">‹</span>
            </button>
        </div>

        <div class="sidebar-content">
            <!-- Search Box -->
            <div class="sidebar-search">
                <input type="text" id="global-search" placeholder="🔍 Search reports..."
                       onkeyup="globalSearch(this.value)" aria-label="Search reports">
            </div>

            <!-- Main Navigation -->
            <ul class="nav-main">
                <li class="{hub_active}">
                    <a href="index.html">
                        <span class="nav-icon">🏠</span>
                        <span class="nav-label">Home</span>
                    </a>
                </li>
                <li class="{accessibility_active}">
                    <a href="accessibility_report.html">
                        <span class="nav-icon">✓</span>
                        <span class="nav-label">Accessibility</span>
                    </a>
                </li>
                <li class="{images_active}">
                    <a href="image_report.html">
                        <span class="nav-icon">📸</span>
                        <span class="nav-label">Images</span>
                    </a>
                </li>
                {f'''<li class="{broken_links_active}">
                    <a href="broken_links_report.html">
                        <span class="nav-icon">🔗</span>
                        <span class="nav-label">Broken Links</span>
                    </a>
                </li>''' if show_broken_links else ''}
            </ul>

            <!-- Pages Section -->
            {f"""
            <div class="nav-section">
                <h3 class="nav-section-title">📄 Pages ({len(page_list)})</h3>
                <ul class="nav-pages">
                    {page_items_html}
                </ul>
            </div>
            """ if page_list else ""}
        </div>
    </nav>'''




def get_sidebar_javascript() -> str:
    """Return JavaScript for sidebar functionality"""
    return '''<script>
        // Sidebar toggle
        function toggleSidebar() {
            const sidebar = document.getElementById('report-sidebar');
            const body = document.body;

            sidebar.classList.toggle('collapsed');
            body.classList.toggle('sidebar-collapsed');

            // Save preference
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        }

        // Load sidebar state
        document.addEventListener('DOMContentLoaded', () => {
            const collapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            if (collapsed) {
                document.getElementById('report-sidebar').classList.add('collapsed');
                document.body.classList.add('sidebar-collapsed');
            }
        });

        // Global search functionality
        function globalSearch(query) {
            const searchTerm = query.toLowerCase().trim();

            if (searchTerm.length === 0) {
                // Reset - show all
                document.querySelectorAll('.nav-pages li').forEach(li => {
                    li.style.display = '';
                });
                return;
            }

            // Filter page list
            document.querySelectorAll('.nav-pages li').forEach(li => {
                const link = li.querySelector('a');
                if (link) {
                    const text = link.textContent.toLowerCase();
                    li.style.display = text.includes(searchTerm) ? '' : 'none';
                }
            });
        }

        // Mobile menu toggle
        function toggleMobileMenu() {
            document.getElementById('report-sidebar').classList.toggle('mobile-open');
        }
    </script>'''


def get_breadcrumb_navigation(
    current_page: str,
    current_page_name: Optional[str] = None,
    page_list: Optional[List[str]] = None,
    show_broken_links: bool = False
) -> str:
    """
    Generate breadcrumb + dropdown navigation bar

    Args:
        current_page: Current page identifier ('hub', 'accessibility', 'images', 'broken_links', 'page_detail')
        current_page_name: Optional page name if on page_detail
        page_list: Optional list of page names for the pages dropdown
        show_broken_links: Whether to show the broken links navigation item

    Returns:
        HTML string for breadcrumb navigation bar
    """
    page_list = page_list or []

    # Build breadcrumb trail based on current page
    breadcrumb_html = ''

    if current_page == 'hub':
        breadcrumb_html = '''
            <span class="nav-breadcrumb-item current">
                <span>🏠</span>
                <span>Home</span>
            </span>'''
    elif current_page == 'accessibility':
        breadcrumb_html = '''
            <a href="index.html" class="nav-breadcrumb-item">
                <span>🏠</span>
                <span>Home</span>
            </a>
            <span class="nav-breadcrumb-separator">›</span>
            <span class="nav-breadcrumb-item current">
                <span>✓</span>
                <span>Accessibility</span>
            </span>'''
    elif current_page == 'images':
        breadcrumb_html = '''
            <a href="index.html" class="nav-breadcrumb-item">
                <span>🏠</span>
                <span>Home</span>
            </a>
            <span class="nav-breadcrumb-separator">›</span>
            <span class="nav-breadcrumb-item current">
                <span>📸</span>
                <span>Images</span>
            </span>'''
    elif current_page == 'broken_links':
        breadcrumb_html = '''
            <a href="index.html" class="nav-breadcrumb-item">
                <span>🏠</span>
                <span>Home</span>
            </a>
            <span class="nav-breadcrumb-separator">›</span>
            <span class="nav-breadcrumb-item current">
                <span>🔗</span>
                <span>Broken Links</span>
            </span>'''
    elif current_page == 'page_detail' and current_page_name:
        display_name = current_page_name[:40] + '...' if len(current_page_name) > 40 else current_page_name
        breadcrumb_html = f'''
            <a href="index.html" class="nav-breadcrumb-item">
                <span>🏠</span>
                <span>Home</span>
            </a>
            <span class="nav-breadcrumb-separator">›</span>
            <a href="accessibility_report.html" class="nav-breadcrumb-item">
                <span>✓</span>
                <span>Accessibility</span>
            </a>
            <span class="nav-breadcrumb-separator">›</span>
            <span class="nav-breadcrumb-item current">
                <span>{display_name}</span>
            </span>'''

    # Build sections dropdown
    sections_items = [
        '<a href="index.html" class="nav-dropdown-item">🏠 Home</a>',
        '<a href="accessibility_report.html" class="nav-dropdown-item">✓ Accessibility</a>',
        '<a href="image_report.html" class="nav-dropdown-item">📸 Images</a>'
    ]

    if show_broken_links:
        sections_items.append('<a href="broken_links_report.html" class="nav-dropdown-item">🔗 Broken Links</a>')

    sections_html = '\n'.join(sections_items)

    # Build pages dropdown
    pages_dropdown_html = ''
    if page_list:
        page_items = []
        for page in sorted(page_list):
            is_current = (current_page == 'page_detail' and current_page_name == page)
            current_class = ' current' if is_current else ''
            page_items.append(f'<a href="{page}_accessibility.html" class="nav-dropdown-item{current_class}">{page}</a>')

        pages_items_html = '\n'.join(page_items)
        pages_dropdown_html = f'''
            <div class="nav-dropdown" id="pages-dropdown">
                <button class="nav-dropdown-toggle"
                        onclick="toggleDropdown('pages-dropdown')"
                        aria-label="View all pages"
                        aria-expanded="false">
                    <span>📄 Pages ({len(page_list)})</span>
                    <span class="nav-dropdown-arrow">▼</span>
                </button>
                <div class="nav-dropdown-menu">
                    <div class="nav-dropdown-search">
                        <input type="text"
                               placeholder="🔍 Filter pages..."
                               onkeyup="filterDropdownItems('pages-dropdown', this.value)"
                               aria-label="Filter pages">
                    </div>
                    <div class="nav-dropdown-items" id="pages-dropdown-items">
                        {pages_items_html}
                    </div>
                </div>
            </div>'''

    return f'''
    <nav class="nav-bar" role="navigation" aria-label="Main navigation">
        <div class="nav-bar-inner">
            <div class="nav-breadcrumb" role="navigation" aria-label="Breadcrumb">
                {breadcrumb_html}
            </div>

            <div class="nav-utilities">
                <div class="nav-dropdown" id="sections-dropdown">
                    <button class="nav-dropdown-toggle"
                            onclick="toggleDropdown('sections-dropdown')"
                            aria-label="View all sections"
                            aria-expanded="false">
                        <span>Sections</span>
                        <span class="nav-dropdown-arrow">▼</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <div class="nav-dropdown-items">
                            {sections_html}
                        </div>
                    </div>
                </div>

                {pages_dropdown_html}
            </div>
        </div>
    </nav>'''


def get_breadcrumb_javascript() -> str:
    """Return JavaScript for breadcrumb navigation functionality (now external)"""
    return '<script src="js/reports.js"></script>'



def get_jump_to_section_links(sections: List[Dict[str, str]]) -> str:
    """
    Generate jump-to-section navigation

    Args:
        sections: List of dicts with 'id' and 'title' keys

    Returns:
        HTML string for jump links
    """
    if not sections:
        return ""

    links = []
    for section in sections:
        links.append(f'<li><a href="#{section["id"]}">{section["title"]}</a></li>')

    return f'''
    <nav class="jump-nav" aria-label="Jump to section">
        <details open>
            <summary>📑 Quick Navigation</summary>
            <ul class="jump-list">
                {''.join(links)}
            </ul>
        </details>
    </nav>'''




def build_breadcrumb(path_items: List[Dict[str, str]]) -> str:
    """
    Build breadcrumb navigation component.

    Args:
        path_items: List of dicts with 'label' and optional 'url' keys.
                   Last item is automatically marked as active.

    Returns:
        HTML string for breadcrumb navigation

    Example:
        build_breadcrumb([
            {'label': 'Home', 'url': 'index.html'},
            {'label': 'Accessibility', 'url': 'accessibility_report.html'},
            {'label': 'Page Detail'}  # No URL = active
        ])
    """
    if not path_items:
        return ""

    items_html = []
    for i, item in enumerate(path_items):
        is_last = (i == len(path_items) - 1)

        if is_last or 'url' not in item:
            # Active/current item
            items_html.append(f'<span class="report-breadcrumb-item active">{item["label"]}</span>')
        else:
            # Clickable link
            items_html.append(f'<a href="{item["url"]}" class="report-breadcrumb-item">{item["label"]}</a>')

        # Add separator (except after last item)
        if not is_last:
            items_html.append('<span class="report-breadcrumb-separator">›</span>')

    return f'<nav class="report-breadcrumb" aria-label="Breadcrumb">{"".join(items_html)}</nav>'


def build_report_header(title: str, subtitle: str = "", timestamp: str = "", breadcrumb: List[Dict[str, str]] = None, centered: bool = False) -> str:
    """
    Build standardized report header component.

    Args:
        title: Main title of the report
        subtitle: Optional subtitle
        timestamp: Optional timestamp string
        breadcrumb: Optional breadcrumb navigation items
        centered: Whether to center the header content

    Returns:
        HTML string for report header
    """
    from datetime import datetime as dt

    # Generate timestamp if not provided
    if not timestamp:
        timestamp = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    # Build breadcrumb if provided
    breadcrumb_html = build_breadcrumb(breadcrumb) if breadcrumb else ""

    centered_class = " centered" if centered else ""
    subtitle_html = f'<p class="report-header-subtitle">{subtitle}</p>' if subtitle else ""

    return f'''
    {breadcrumb_html}
    <header class="report-header{centered_class}">
        <h1 class="report-header-title">{title}</h1>
        {subtitle_html}
        <p class="report-header-timestamp">Generated: {timestamp}</p>
    </header>'''


def build_stat_cards(stats: List[Dict[str, any]], grid_size: str = "default") -> str:
    """
    Build grid of statistic cards.

    Args:
        stats: List of dicts with 'value', 'label', and optional 'color' keys
        grid_size: Grid sizing - 'narrow', 'default', 'medium', or 'wide'

    Returns:
        HTML string for stat cards grid

    Example:
        build_stat_cards([
            {'value': 42, 'label': 'Total Pages'},
            {'value': '95%', 'label': 'WCAG AA', 'color': '#28a745'}
        ])
    """
    if not stats:
        return ""

    grid_class = f"report-grid {grid_size}" if grid_size != "default" else "report-grid"

    cards_html = []
    for stat in stats:
        value = stat.get('value', 0)
        label = stat.get('label', '')
        color = stat.get('color', '')

        # Apply color if provided
        value_style = f' style="color: {color};"' if color else ''

        cards_html.append(f'''
        <div class="report-card stat no-hover">
            <div class="report-card-stat-value"{value_style}>{value}</div>
            <div class="report-card-stat-label">{label}</div>
        </div>''')

    return f'<div class="{grid_class}">{"".join(cards_html)}</div>'


def build_data_table(headers: List[Dict[str, any]], rows: List[List[str]], sortable: bool = False, table_id: str = "data-table") -> str:
    """
    Build standardized data table component.

    Args:
        headers: List of dicts with 'label' and optional 'align', 'sortable' keys
        rows: List of row data (list of cell values)
        sortable: Enable sortable columns
        table_id: Unique ID for the table

    Returns:
        HTML string for data table

    Example:
        build_data_table(
            headers=[
                {'label': 'Page', 'align': 'left'},
                {'label': 'Score', 'align': 'center', 'sortable': True}
            ],
            rows=[
                ['Page 1', '95%'],
                ['Page 2', '87%']
            ]
        )
    """
    if not headers or not rows:
        return ""

    # Build header cells
    header_cells = []
    for header in headers:
        label = header.get('label', '')
        align = header.get('align', 'left')
        is_sortable = sortable and header.get('sortable', False)

        align_class = f' class="{align}"' if align != 'left' else ''
        sortable_class = ' sortable' if is_sortable else ''

        header_cells.append(f'<th{align_class}{sortable_class}>{label}</th>')

    # Build body rows
    body_rows = []
    for row in rows:
        cells = ''.join([f'<td>{cell}</td>' for cell in row])
        body_rows.append(f'<tr>{cells}</tr>')

    return f'''
    <div class="report-table-wrapper">
        <table class="report-table" id="{table_id}">
            <thead>
                <tr>{"".join(header_cells)}</tr>
            </thead>
            <tbody>
                {"".join(body_rows)}
            </tbody>
        </table>
    </div>'''


def build_filter_bar(filters: List[Dict[str, any]]) -> str:
    """
    Build filter control bar component.

    Args:
        filters: List of filter configs with 'type', 'id', 'label', 'options' keys

    Returns:
        HTML string for filter bar

    Example:
        build_filter_bar([
            {
                'type': 'select',
                'id': 'status-filter',
                'label': 'Status',
                'options': [
                    {'value': 'all', 'label': 'All'},
                    {'value': 'success', 'label': 'Success'}
                ]
            }
        ])
    """
    if not filters:
        return ""

    filter_groups = []
    for filter_config in filters:
        filter_type = filter_config.get('type', 'select')
        filter_id = filter_config.get('id', 'filter')
        label = filter_config.get('label', '')

        if filter_type == 'select':
            options = filter_config.get('options', [])
            options_html = ''.join([
                f'<option value="{opt.get("value", "")}">{opt.get("label", "")}</option>'
                for opt in options
            ])

            filter_groups.append(f'''
            <div class="report-filter-group">
                <label class="report-filter-label" for="{filter_id}">{label}:</label>
                <select class="report-filter-select" id="{filter_id}">
                    {options_html}
                </select>
            </div>''')

        elif filter_type == 'input':
            placeholder = filter_config.get('placeholder', '')
            filter_groups.append(f'''
            <div class="report-filter-group">
                <label class="report-filter-label" for="{filter_id}">{label}:</label>
                <input type="text" class="report-filter-input" id="{filter_id}" placeholder="{placeholder}">
            </div>''')

    return f'<div class="report-filter-bar">{"".join(filter_groups)}</div>'


def build_action_buttons(actions: List[Dict[str, str]]) -> str:
    """
    Build action buttons component.

    Args:
        actions: List of dicts with 'label', 'url', optional 'style', 'icon' keys

    Returns:
        HTML string for action buttons

    Example:
        build_action_buttons([
            {'label': 'View HTML', 'url': 'page.html', 'icon': '📄'},
            {'label': 'Download DOCX', 'url': 'page.docx', 'icon': '📝'}
        ])
    """
    if not actions:
        return ""

    buttons_html = []
    for action in actions:
        label = action.get('label', '')
        url = action.get('url', '#')
        icon = action.get('icon', '')
        style = action.get('style', '')  # 'secondary', 'success'
        target = action.get('target', '_blank') if action.get('external', False) else ''
        download = ' download' if action.get('download', False) else ''

        style_class = f' {style}' if style else ''
        target_attr = f' target="{target}" rel="noopener noreferrer"' if target else ''
        icon_html = f'{icon} ' if icon else ''
        aria_label = action.get('aria_label', label)

        buttons_html.append(
            f'<a href="{url}" class="report-action-link{style_class}"{target_attr}{download} '
            f'aria-label="{aria_label}">{icon_html}{label}</a>'
        )

    return f'<nav class="report-actions" aria-label="Page actions">{"".join(buttons_html)}</nav>'


def build_empty_state(icon: str, message: str, hint: str = "") -> str:
    """
    Build empty state component.

    Args:
        icon: Emoji or icon for empty state
        message: Main message
        hint: Optional hint text

    Returns:
        HTML string for empty state
    """
    hint_html = f'<p class="report-empty-state-hint">{hint}</p>' if hint else ""

    return f'''
    <div class="report-empty-state">
        <div class="report-empty-state-icon">{icon}</div>
        <p class="report-empty-state-message">{message}</p>
        {hint_html}
    </div>'''


def build_alert(message: str, alert_type: str = "info") -> str:
    """
    Build alert/notice component.

    Args:
        message: Alert message
        alert_type: Type of alert - 'success', 'warning', 'danger', 'info'

    Returns:
        HTML string for alert
    """
    return f'<div class="report-alert {alert_type}" role="alert">{message}</div>'


if __name__ == '__main__':
    print("Report components module loaded successfully")
