#!/usr/bin/env python3
"""
Template Renderer - Replaces string concatenation with proper Jinja2 templates

Fixes the "spaghetti HTML" problem by using templates instead of Python string building.
This ensures:
- Clean, properly formatted HTML output
- Separation of data and presentation
- Reusable components across all reports
- Maintainable code
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup


class TemplateRenderer:
    """Render reports using Jinja2 templates"""

    def __init__(self, output_dir: str = "output"):
        """Initialize template renderer.

        Args:
            output_dir: Root output directory
        """
        self.output_dir = Path(output_dir)
        template_dir = Path(__file__).parent / "templates"

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render_page_report(
        self,
        page_name: str,
        html_report: Dict[str, Any],
        docx_report: Dict[str, Any],
        css_links: str,
        navigation: str,
        breadcrumb: str,
        header: str,
        actions: List[Dict[str, str]]
    ) -> str:
        """Render a page accessibility report.

        Args:
            page_name: Name of the page
            html_report: HTML version accessibility data
            docx_report: DOCX version accessibility data
            css_links: CSS link tags
            navigation: Navigation HTML
            breadcrumb: Breadcrumb HTML
            header: Header HTML
            actions: List of action buttons

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("page_report.html")

        # Helper to format issues
        def format_issues(issue_list, level='error'):
            formatted = []
            if isinstance(issue_list, list):
                for issue in issue_list:
                    if isinstance(issue, dict):
                        formatted.append(issue)
                    else:
                        formatted.append({
                            'code': '',
                            'message': str(issue),
                            'level': level
                        })
            return formatted

        # Get scores
        html_aa = html_report.get('score_aa', 0)
        html_aaa = html_report.get('score_aaa', 0)
        docx_aa = docx_report.get('score_aa', 0)
        docx_aaa = docx_report.get('score_aaa', 0)

        # Prepare versions data
        versions = [
            {
                "icon": "📄",
                "title": "HTML Version",
                "status": "success",
                "scores": [
                    {
                        "value": f"{html_aa}%",
                        "class": "success" if html_aa >= 80 else "warning"
                    },
                    {
                        "value": f"{html_aaa}%",
                        "class": "success" if html_aaa >= 80 else "danger"
                    }
                ],
                "issues": format_issues(html_report.get('issues_aa', []), 'error') +
                         format_issues(html_report.get('issues_aaa', []), 'error-aaa') +
                         format_issues(html_report.get('warnings', []), 'warning')
            },
            {
                "icon": "📝",
                "title": "DOCX Version",
                "status": "success",
                "scores": [
                    {
                        "value": f"{docx_aa}%",
                        "class": "success" if docx_aa >= 80 else "warning"
                    },
                    {
                        "value": f"{docx_aaa}%",
                        "class": "success" if docx_aaa >= 80 else "danger"
                    }
                ],
                "issues": format_issues(docx_report.get('issues_aa', []), 'error') +
                         format_issues(docx_report.get('issues_aaa', []), 'error-aaa') +
                         format_issues(docx_report.get('warnings', []), 'warning')
            }
        ]

        return template.render(
            page_name=page_name,
            css_links=Markup(css_links),
            navigation=Markup(navigation),
            breadcrumb=Markup(breadcrumb),
            header=Markup(header),
            actions=actions,
            versions=versions
        )

    def render_image_report(self, css_links: str, navigation: str, header: str,
                            statistics: str, page_options: str, type_options: str,
                            image_table: str, breadcrumb_javascript: str) -> str:
        """Render image report template.

        Args:
            css_links: CSS link tags
            navigation: Navigation HTML
            header: Header HTML
            statistics: Statistics HTML
            page_options: Page filter options HTML
            type_options: Type filter options HTML
            image_table: Image table HTML
            breadcrumb_javascript: Breadcrumb JavaScript

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("image_report.html")
        return template.render(
            css_links=Markup(css_links),
            navigation=Markup(navigation),
            header=Markup(header),
            statistics=Markup(statistics),
            page_options=Markup(page_options),
            type_options=Markup(type_options),
            image_table=Markup(image_table),
            breadcrumb_javascript=Markup(breadcrumb_javascript)
        )

    def render_image_report_v2(self, css_links: str, navigation: str, header: str,
                              summary_stats: str, images_json: str,
                              breadcrumb_javascript: str) -> str:
        """Render modern image report v2 with detail view.

        Args:
            css_links: CSS link tags
            navigation: Navigation HTML
            header: Header HTML
            summary_stats: Summary statistics HTML
            images_json: Images data as JSON string
            breadcrumb_javascript: Breadcrumb JavaScript

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("image_report_v2.html")
        return template.render(
            css_links=Markup(css_links),
            navigation=Markup(navigation),
            header=Markup(header),
            summary_stats=Markup(summary_stats),
            images_json=images_json,
            breadcrumb_javascript=Markup(breadcrumb_javascript)
        )

    def render_landing_hub(self, css_links: str, navigation: str, header: str,
                           jump_links: str, critical_issues: str, statistics: str,
                           navigation_tiles: str, breadcrumb_javascript: str,
                           hub_javascript: str) -> str:
        """Render landing hub template.

        Args:
            css_links: CSS link tags
            navigation: Navigation HTML
            header: Header HTML
            jump_links: Jump-to-section links HTML
            critical_issues: Critical issues section HTML
            statistics: Statistics section HTML
            navigation_tiles: Navigation tiles HTML
            breadcrumb_javascript: Breadcrumb JavaScript
            hub_javascript: Hub-specific JavaScript

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("landing_hub.html")
        return template.render(
            css_links=Markup(css_links),
            navigation=Markup(navigation),
            header=Markup(header),
            jump_links=Markup(jump_links),
            critical_issues=Markup(critical_issues),
            statistics=Markup(statistics),
            navigation_tiles=Markup(navigation_tiles),
            breadcrumb_javascript=Markup(breadcrumb_javascript),
            hub_javascript=Markup(hub_javascript)
        )

    def render_accessibility_dashboard(self, pages: List[Dict[str, Any]], css_links: str,
                                      navigation: str, header: str, stats: str,
                                      breadcrumb_javascript: str) -> str:
        """Render accessibility dashboard template.

        Args:
            pages: List of page data with scores
            css_links: CSS link tags
            navigation: Navigation HTML
            header: Header HTML
            stats: Statistics HTML
            breadcrumb_javascript: Breadcrumb JavaScript

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("accessibility_dashboard.html")
        return template.render(
            pages=pages,
            css_links=Markup(css_links),
            navigation=Markup(navigation),
            header=Markup(header),
            stats=Markup(stats),
            breadcrumb_javascript=Markup(breadcrumb_javascript)
        )

    def render_broken_links_report(self, links: List[Dict[str, Any]], css_links: str,
                                   navigation: str, header: str, stats: str) -> str:
        """Render broken links report template.

        Args:
            links: List of broken links with target, count, sources
            css_links: CSS link tags
            navigation: Navigation HTML
            header: Header HTML
            stats: Statistics HTML

        Returns:
            Rendered HTML string
        """
        template = self.env.get_template("broken_links_report.html")

        # Format links for template
        formatted_links = []
        for link in links:
            sources = link.get('referenced_by', '').split(',') if link.get('referenced_by') else []
            formatted_links.append({
                'target': link['target_page_id'],
                'count': link['reference_count'],
                'sources': [s.strip() for s in sources]
            })

        return template.render(
            links=formatted_links,
            css_links=Markup(css_links),
            navigation=Markup(navigation),
            header=Markup(header),
            stats=Markup(stats)
        )
