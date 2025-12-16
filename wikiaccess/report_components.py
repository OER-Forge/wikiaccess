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




if __name__ == '__main__':
    print("Report components module loaded successfully")
