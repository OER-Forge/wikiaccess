"""
Link Rewriter for WikiAccess

Rewrites internal wiki links in generated HTML files to point to local HTML files.
Tracks links in the database and identifies broken links (missing target pages).
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from urllib.parse import urlparse, parse_qs, unquote
import re
from bs4 import BeautifulSoup


class LinkRewriter:
    """Rewrites internal wiki links to local HTML paths."""

    def __init__(self, wiki_url: str, output_dir: str, db=None):
        """
        Initialize link rewriter.

        Args:
            wiki_url: Base URL of the wiki (e.g., https://example.org/wiki)
            output_dir: Output directory containing HTML files
            db: Optional ConversionDatabase instance for tracking links
        """
        self.wiki_url = wiki_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.html_dir = self.output_dir / 'html'
        self.db = db

        # Parse wiki URL to extract domain
        parsed = urlparse(wiki_url)
        self.wiki_domain = f"{parsed.scheme}://{parsed.netloc}"

        # Track statistics
        self.stats = {
            'files_processed': 0,
            'links_found': 0,
            'links_rewritten': 0,
            'links_broken': 0,
            'external_links': 0
        }

    def extract_page_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract DokuWiki page ID from a URL.

        Args:
            url: URL to parse (e.g., https://wiki.org/doku.php?id=foo:bar)

        Returns:
            Page ID (e.g., 'foo:bar') or None if not a wiki URL
        """
        if not url:
            return None

        # Check if it's a URL from our wiki
        if not url.startswith(self.wiki_domain):
            return None

        # Parse DokuWiki URL format: /doku.php?id=page_id
        if 'doku.php' in url:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            page_id = query_params.get('id', [''])[0]

            # Remove anchor if present
            if '#' in page_id:
                page_id = page_id.split('#')[0]

            # Remove leading colon if present (DokuWiki format quirk)
            page_id = page_id.lstrip(':')

            return page_id if page_id else None

        return None

    def page_id_to_filename(self, page_id: str) -> str:
        """
        Convert page ID to local HTML filename.

        Args:
            page_id: DokuWiki page ID (e.g., 'foo:bar')

        Returns:
            HTML filename (e.g., 'foo_bar.html')
        """
        # Replace colons with underscores and add .html extension
        filename = page_id.replace(':', '_') + '.html'
        return filename

    def get_available_pages(self) -> Set[str]:
        """
        Get set of available HTML files (converted pages).

        Returns:
            Set of filenames (without .html extension) that have been converted
        """
        if not self.html_dir.exists():
            return set()

        # Return filenames (without extension), not page IDs
        # We'll convert target page IDs to filenames for comparison
        available = set()
        for html_file in self.html_dir.glob('*.html'):
            available.add(html_file.stem)  # e.g., '183_notes_momentum_principle'

        return available

    def rewrite_links_in_html(
        self,
        html_path: Path,
        available_pages: Set[str],
        batch_id: Optional[str] = None
    ) -> Tuple[int, int, int]:
        """
        Rewrite links in a single HTML file.

        Args:
            html_path: Path to HTML file
            available_pages: Set of available page IDs
            batch_id: Optional batch ID for database tracking

        Returns:
            Tuple of (links_found, links_rewritten, links_broken)
        """
        # Read HTML file
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        links_found = 0
        links_rewritten = 0
        links_broken = 0

        # Extract source page ID from filename
        source_page_id = html_path.stem.replace('_', ':')

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            links_found += 1

            # Extract page ID from URL
            target_page_id = self.extract_page_id_from_url(href)

            if target_page_id:
                # This is an internal wiki link

                # Extract anchor if present
                anchor = ''
                if '#' in href:
                    anchor = '#' + href.split('#', 1)[1]

                # Convert target page ID to expected filename (without extension)
                target_filename = self.page_id_to_filename(target_page_id).replace('.html', '')

                # Check if target page exists
                if target_filename in available_pages:
                    # Rewrite to local HTML file
                    new_href = self.page_id_to_filename(target_page_id) + anchor
                    link['href'] = new_href
                    links_rewritten += 1

                    # Track in database
                    if self.db and batch_id:
                        self.db.add_link({
                            'source_page_id': source_page_id,
                            'target_page_id': target_page_id,
                            'link_text': link.get_text(strip=True)[:200],
                            'link_type': 'internal',
                            'resolution_status': 'found',
                            'batch_id': batch_id
                        })
                else:
                    # Broken link - target page not converted
                    links_broken += 1

                    # Track in database
                    if self.db and batch_id:
                        self.db.add_link({
                            'source_page_id': source_page_id,
                            'target_page_id': target_page_id,
                            'link_text': link.get_text(strip=True)[:200],
                            'link_type': 'internal',
                            'resolution_status': 'missing',
                            'batch_id': batch_id
                        })
            else:
                # External link - track in database
                if self.db and batch_id and href.startswith('http'):
                    # Extract domain for tracking
                    parsed = urlparse(href)
                    external_domain = f"{parsed.scheme}://{parsed.netloc}"

                    self.db.add_link({
                        'source_page_id': source_page_id,
                        'target_page_id': external_domain,
                        'link_text': link.get_text(strip=True)[:200],
                        'link_type': 'external',
                        'resolution_status': 'external',
                        'batch_id': batch_id
                    })

        # Write modified HTML back
        if links_rewritten > 0:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))

        return links_found, links_rewritten, links_broken

    def rewrite_all_links(self, batch_id: Optional[str] = None) -> Dict[str, int]:
        """
        Rewrite links in all HTML files in the output directory.

        Args:
            batch_id: Optional batch ID for database tracking

        Returns:
            Dictionary with statistics
        """
        if not self.html_dir.exists():
            print(f"HTML directory not found: {self.html_dir}")
            return self.stats

        # Get list of available pages
        available_pages = self.get_available_pages()
        print(f"Found {len(available_pages)} converted pages")

        # Process each HTML file
        for html_file in self.html_dir.glob('*.html'):
            print(f"Processing: {html_file.name}")

            try:
                found, rewritten, broken = self.rewrite_links_in_html(
                    html_file,
                    available_pages,
                    batch_id
                )

                self.stats['files_processed'] += 1
                self.stats['links_found'] += found
                self.stats['links_rewritten'] += rewritten
                self.stats['links_broken'] += broken

                if rewritten > 0 or broken > 0:
                    print(f"  Links: {found} found, {rewritten} rewritten, {broken} broken")

            except Exception as e:
                print(f"  Error processing {html_file.name}: {e}")

        return self.stats

    def generate_broken_links_report(self, batch_id: str, page_list: list = None) -> Optional[str]:
        """
        Generate a report of broken links with consistent styling and navigation.

        Args:
            batch_id: Batch ID to report on
            page_list: Optional list of page names for sidebar navigation

        Returns:
            Path to generated report HTML file, or None if no database
        """
        if not self.db:
            print("No database connection - cannot generate broken links report")
            return None

        broken_links = self.db.get_broken_links(batch_id)

        if not broken_links:
            print("No broken links found!")
            return None

        # Import report components
        try:
            from .report_components import get_navigation_sidebar, get_sidebar_javascript
            from .static_helper import get_css_links
        except ImportError:
            print("Warning: Could not import report components, generating standalone report")
            return self._generate_standalone_report(broken_links)

        # Generate HTML report with navigation sidebar
        reports_dir = self.output_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / 'broken_links_report.html'

        # Build navigation sidebar
        sidebar_html = get_navigation_sidebar('broken_links', page_list or [], show_broken_links=True)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Broken Links Report - WikiAccess</title>
{get_css_links()}
</head>
<body class="has-sidebar">
    {sidebar_html}

    <button class="mobile-menu-btn" onclick="toggleMobileMenu()">☰ Menu</button>

    <div class="main-content">
        <header>
            <h1>🔗 Broken Links Report</h1>
            <p class="subtitle">Internal wiki links pointing to pages that haven't been converted</p>
        </header>

        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-stats">
                <div class="stat">
                    <span class="stat-value">{len(broken_links)}</span>
                    <span class="stat-label">Broken Links</span>
                </div>
                <div class="stat">
                    <span class="stat-value">{sum(link['reference_count'] for link in broken_links)}</span>
                    <span class="stat-label">Total References</span>
                </div>
            </div>
        </div>

        <div class="broken-links-grid">
"""

        for link in broken_links:
            target = link['target_page_id']
            count = link['reference_count']
            sources = link['referenced_by'].split(',')

            sources_html = '\n'.join([f'<span class="source-tag">{source.strip()}</span>' for source in sources])

            html += f"""
            <div class="broken-link">
                <div class="target">Missing Page: {target}</div>
                <div class="references">
                    <span class="ref-count">{count} {('reference' if count == 1 else 'references')}</span>
                    <div class="ref-sources">
                        <strong>Referenced by:</strong>
                        <div class="source-list">
                            {sources_html}
                        </div>
                    </div>
                </div>
            </div>
"""

        html += f"""
        </div>
    </div>

    {get_sidebar_javascript()}
</body>
</html>
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\nBroken links report: {report_path}")
        return str(report_path)

    def _generate_standalone_report(self, broken_links: list) -> str:
        """Fallback method to generate standalone report without shared components"""
        reports_dir = self.output_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / 'broken_links_report.html'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Broken Links Report - WikiAccess</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{ color: #d32f2f; }}
        .broken-link {{
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #d32f2f;
        }}
    </style>
</head>
<body>
    <h1>Broken Links Report</h1>
    <p>Total: {len(broken_links)}</p>
"""
        for link in broken_links:
            html += f'<div class="broken-link"><strong>{link["target_page_id"]}</strong> ({link["reference_count"]} references)</div>'
        html += "</body></html>"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return str(report_path)
