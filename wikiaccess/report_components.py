#!/usr/bin/env python3
"""
WikiAccess - Shared Report Components

Reusable UI components for reports including navigation sidebar,
search functionality, and common styling.
"""

from typing import List, Dict, Optional


def get_navigation_sidebar(current_page: str, page_list: Optional[List[str]] = None) -> str:
    """
    Generate persistent navigation sidebar for all reports

    Args:
        current_page: Current page identifier ('hub', 'accessibility', 'images', 'page_detail')
        page_list: Optional list of page names for the pages section

    Returns:
        HTML string for navigation sidebar
    """
    page_list = page_list or []

    # Determine active state
    hub_active = "active" if current_page == "hub" else ""
    accessibility_active = "active" if current_page == "accessibility" else ""
    images_active = "active" if current_page == "images" else ""
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


def get_sidebar_css() -> str:
    """Return CSS for navigation sidebar"""
    return '''<style>
        /* Sidebar Navigation */
        .report-sidebar {
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            width: 280px;
            background: #2c3e50;
            color: white;
            overflow-y: auto;
            transition: transform 0.3s ease;
            z-index: 1000;
            box-shadow: 2px 0 8px rgba(0,0,0,0.15);
        }

        .report-sidebar.collapsed {
            transform: translateX(-240px);
        }

        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.5rem;
            background: #34495e;
            border-bottom: 2px solid #1a252f;
        }

        .sidebar-header h2 {
            margin: 0;
            font-size: 1.3em;
            color: white;
        }

        .sidebar-toggle {
            background: transparent;
            border: 2px solid #7f8c8d;
            color: white;
            cursor: pointer;
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .sidebar-toggle:hover {
            background: #7f8c8d;
            border-color: #95a5a6;
        }

        .toggle-icon {
            font-size: 1.5em;
            font-weight: bold;
            transition: transform 0.3s ease;
        }

        .report-sidebar.collapsed .toggle-icon {
            transform: rotate(180deg);
        }

        .sidebar-content {
            padding: 1rem;
        }

        .sidebar-search {
            margin-bottom: 1.5rem;
        }

        .sidebar-search input {
            width: 100%;
            padding: 0.75rem;
            background: #34495e;
            border: 2px solid #7f8c8d;
            border-radius: 4px;
            color: white;
            font-size: 0.9em;
        }

        .sidebar-search input:focus {
            outline: none;
            border-color: #3498db;
            background: #2c3e50;
        }

        .sidebar-search input::placeholder {
            color: #95a5a6;
        }

        .nav-main {
            list-style: none;
            padding: 0;
            margin: 0 0 1.5rem 0;
        }

        .nav-main li {
            margin-bottom: 0.5rem;
        }

        .nav-main a {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            color: #ecf0f1;
            text-decoration: none;
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .nav-main a:hover {
            background: #34495e;
            color: white;
        }

        .nav-main li.active a {
            background: #3498db;
            color: white;
            font-weight: 600;
        }

        .nav-icon {
            font-size: 1.3em;
            margin-right: 0.75rem;
            width: 24px;
            text-align: center;
        }

        .nav-label {
            flex: 1;
        }

        .nav-section {
            border-top: 1px solid #34495e;
            padding-top: 1rem;
            margin-top: 1rem;
        }

        .nav-section-title {
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #95a5a6;
            margin: 0 0 0.75rem 0.5rem;
            font-weight: 600;
        }

        .nav-pages {
            list-style: none;
            padding: 0;
            margin: 0;
            max-height: 400px;
            overflow-y: auto;
        }

        .nav-pages li {
            margin-bottom: 0.25rem;
        }

        .nav-pages a {
            display: block;
            padding: 0.5rem 1rem;
            color: #bdc3c7;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
            transition: all 0.2s ease;
        }

        .nav-pages a:hover {
            background: #34495e;
            color: white;
        }

        .more-pages {
            font-style: italic;
            color: #7f8c8d;
            font-size: 0.85em;
            padding: 0.5rem 1rem;
        }

        /* Main content adjustment for sidebar */
        body.has-sidebar {
            margin-left: 280px;
            transition: margin-left 0.3s ease;
        }

        body.has-sidebar.sidebar-collapsed {
            margin-left: 40px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .report-sidebar {
                width: 100%;
                transform: translateX(-100%);
            }

            .report-sidebar.mobile-open {
                transform: translateX(0);
            }

            body.has-sidebar {
                margin-left: 0;
            }

            .mobile-menu-btn {
                display: block;
                position: fixed;
                top: 1rem;
                left: 1rem;
                z-index: 999;
                background: #3498db;
                color: white;
                border: none;
                padding: 0.75rem;
                border-radius: 4px;
                cursor: pointer;
            }
        }

        .mobile-menu-btn {
            display: none;
        }
    </style>'''


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


def get_jump_nav_css() -> str:
    """Return CSS for jump navigation"""
    return '''<style>
        .jump-nav {
            background: #e7f3ff;
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 2rem;
        }

        .jump-nav summary {
            cursor: pointer;
            font-weight: 600;
            color: #2c3e50;
            user-select: none;
            padding: 0.5rem;
        }

        .jump-nav summary:hover {
            color: #3498db;
        }

        .jump-list {
            list-style: none;
            padding: 0;
            margin: 1rem 0 0 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
        }

        .jump-list a {
            display: block;
            padding: 0.5rem 1rem;
            background: white;
            border-radius: 4px;
            color: #3498db;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .jump-list a:hover {
            background: #3498db;
            color: white;
            transform: translateX(4px);
        }
    </style>'''


if __name__ == '__main__':
    print("Report components module loaded successfully")
