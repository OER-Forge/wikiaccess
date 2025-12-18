"""
Discovery CLI - Interactive interface for reviewing and managing discovered pages.

Allows users to:
- Review discovered pages one by one
- Approve or skip pages
- Check page availability
- View source pages that reference each discovery
- Perform bulk operations (approve/skip by criteria)
- Export discovered pages to file
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from .database import ConversionDatabase
from .discovery import PageDiscoveryEngine

logger = logging.getLogger(__name__)


class DiscoveryCLI:
    """Interactive CLI for reviewing discovered pages."""

    def __init__(self, db_path: str = "output/conversion_history.db"):
        """Initialize the CLI."""
        self.db = ConversionDatabase(db_path)
        self.current_index = 0
        self.discovered_pages: List[Dict[str, Any]] = []
        self.wiki_url = None

    def run(self):
        """Start the interactive review loop."""
        print("\n" + "="*70)
        print("WikiAccess Discovery Review CLI")
        print("="*70 + "\n")

        # Load discovered pages
        self.discovered_pages = self.db.get_discovered_pages(status='discovered')

        if not self.discovered_pages:
            print("✓ No discovered pages to review!")
            return

        # Get wiki URL from first batch
        if self.discovered_pages:
            self.wiki_url = self.discovered_pages[0].get('wiki_url', 'https://wiki.example.com')

        print(f"Found {len(self.discovered_pages)} pages to review")
        print("Navigation: [a]pprove, [s]kip, [c]heck, [v]iew sources, [n]ext, [p]revious, [q]uit, [b]ulk")
        print()

        self._review_loop()

    def _review_loop(self):
        """Main review loop."""
        while self.current_index < len(self.discovered_pages):
            page_data = self.discovered_pages[self.current_index]
            self._display_page(page_data)

            while True:
                action = input("\nAction (a/s/c/v/n/p/q/b/h): ").strip().lower()

                if action == 'a':
                    self._approve_page(page_data)
                    self.current_index += 1
                    break
                elif action == 's':
                    self._skip_page(page_data)
                    self.current_index += 1
                    break
                elif action == 'c':
                    self._check_page(page_data)
                elif action == 'v':
                    self._view_sources(page_data)
                elif action == 'n':
                    self.current_index += 1
                    break
                elif action == 'p':
                    if self.current_index > 0:
                        self.current_index -= 1
                    break
                elif action == 'q':
                    print("\nExiting...")
                    return
                elif action == 'b':
                    self._bulk_menu()
                elif action == 'h':
                    self._show_help()
                else:
                    print("Invalid action")

    def _display_page(self, page_data: Dict[str, Any]):
        """Display a discovered page."""
        page_id = page_data['target_page_id']
        depth = page_data['discovery_depth']
        refs = page_data['reference_count']
        status = page_data['discovery_status']

        progress = f"{self.current_index + 1}/{len(self.discovered_pages)}"

        print(f"\n{'-'*70}")
        print(f"[{progress}] {page_id}")
        print(f"{'-'*70}")
        print(f"  Depth: {depth} | References: {refs} | Status: {status}")

        url = self._build_url(page_id)
        print(f"  URL: {url}")

    def _approve_page(self, page_data: Dict[str, Any]):
        """Approve a page for conversion."""
        page_id = page_data['target_page_id']
        reason = input("Optional reason for approval (or Enter to skip): ").strip() or None
        self.db.update_discovery_status(page_id, 'approved', reason)
        print(f"✓ Approved: {page_id}")

    def _skip_page(self, page_data: Dict[str, Any]):
        """Skip a page permanently."""
        page_id = page_data['target_page_id']
        reason = input("Reason for skipping (or Enter for 'user skip'): ").strip() or "user skip"
        self.db.update_discovery_status(page_id, 'skipped', reason)
        print(f"✗ Skipped: {page_id}")

    def _check_page(self, page_data: Dict[str, Any]):
        """Check if a page exists on the wiki."""
        page_id = page_data['target_page_id']
        print(f"\nChecking {page_id}...")

        try:
            engine = PageDiscoveryEngine(self.db, self.wiki_url or '')
            exists, status = engine.check_page_exists(page_id)
            engine.close()

            if status == 200:
                print(f"✓ Page exists (HTTP 200)")
            elif status == 404:
                print(f"✗ Page not found (HTTP 404)")
                auto_mark = input("Mark as failed_404? (y/n): ").strip().lower()
                if auto_mark == 'y':
                    self.db.update_discovery_status(
                        page_id, 'failed_404',
                        reason='HTTP 404 - Page not found',
                        http_status=404
                    )
                    print("✓ Marked as failed_404")
            else:
                print(f"? Got HTTP {status}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def _view_sources(self, page_data: Dict[str, Any]):
        """View source pages that reference this discovery."""
        discovered_id = page_data['id']
        sources = self.db.get_discovery_sources(discovered_id)

        if not sources:
            print("No sources found")
            return

        print(f"\nPages linking to {page_data['target_page_id']}:")
        print("-" * 50)
        for source in sources:
            print(f"  • {source['source_page_id']}")
            if source['link_text']:
                print(f"    Link text: {source['link_text'][:60]}")

    def _bulk_menu(self):
        """Show bulk operations menu."""
        print("\nBulk Operations:")
        print("  [1] Approve all discovered pages")
        print("  [2] Skip all discovered pages")
        print("  [3] Approve by namespace")
        print("  [4] Approve by minimum references")
        print("  [5] Check all for 404s")
        print("  [6] Export to file")
        print("  [q] Back")

        action = input("\nChoice: ").strip().lower()

        if action == '1':
            self._bulk_approve_all()
        elif action == '2':
            self._bulk_skip_all()
        elif action == '3':
            self._bulk_approve_namespace()
        elif action == '4':
            self._bulk_approve_min_refs()
        elif action == '5':
            self._bulk_check_404s()
        elif action == '6':
            self._export_discovered()

    def _bulk_approve_all(self):
        """Approve all discovered pages."""
        confirm = input(f"Approve all {len(self.discovered_pages)} pages? (y/n): ").strip().lower()
        if confirm != 'y':
            return

        page_ids = [p['target_page_id'] for p in self.discovered_pages]
        self.db.bulk_update_discovery_status(page_ids, 'approved', 'Bulk approved')
        print(f"✓ Approved {len(page_ids)} pages")

    def _bulk_skip_all(self):
        """Skip all discovered pages."""
        confirm = input(f"Skip all {len(self.discovered_pages)} pages? (y/n): ").strip().lower()
        if confirm != 'y':
            return

        page_ids = [p['target_page_id'] for p in self.discovered_pages]
        self.db.bulk_update_discovery_status(page_ids, 'skipped', 'Bulk skipped')
        print(f"✓ Skipped {len(page_ids)} pages")

    def _bulk_approve_namespace(self):
        """Approve all pages matching a namespace pattern."""
        namespace = input("Enter namespace pattern (e.g., '183_notes:examples:*'): ").strip()
        if not namespace:
            return

        # Convert wildcard pattern to matching logic
        namespace_prefix = namespace.rstrip('*')
        matching = [p for p in self.discovered_pages if p['target_page_id'].startswith(namespace_prefix)]

        if not matching:
            print("No matching pages found")
            return

        print(f"Found {len(matching)} matching pages")
        for page in matching:
            print(f"  • {page['target_page_id']}")

        confirm = input(f"\nApprove {len(matching)} pages? (y/n): ").strip().lower()
        if confirm != 'y':
            return

        page_ids = [p['target_page_id'] for p in matching]
        self.db.bulk_update_discovery_status(page_ids, 'approved', f'Bulk approved: {namespace}')
        print(f"✓ Approved {len(page_ids)} pages")

    def _bulk_approve_min_refs(self):
        """Approve pages with minimum reference count."""
        try:
            min_refs = int(input("Minimum references: ").strip())
        except ValueError:
            print("Invalid number")
            return

        matching = [p for p in self.discovered_pages if p['reference_count'] >= min_refs]

        if not matching:
            print("No matching pages found")
            return

        print(f"Found {len(matching)} pages with {min_refs}+ references")
        confirm = input(f"Approve {len(matching)} pages? (y/n): ").strip().lower()
        if confirm != 'y':
            return

        page_ids = [p['target_page_id'] for p in matching]
        self.db.bulk_update_discovery_status(page_ids, 'approved', f'Bulk approved: >{min_refs} refs')
        print(f"✓ Approved {len(page_ids)} pages")

    def _bulk_check_404s(self):
        """Check all discovered pages for 404s."""
        confirm = input(f"Check {len(self.discovered_pages)} pages for 404? (y/n): ").strip().lower()
        if confirm != 'y':
            return

        print("\nChecking pages...")
        engine = PageDiscoveryEngine(self.db, self.wiki_url or '')

        found_404 = 0
        for i, page in enumerate(self.discovered_pages):
            page_id = page['target_page_id']
            exists, status = engine.check_page_exists(page_id)

            if status == 404:
                self.db.update_discovery_status(
                    page_id, 'failed_404',
                    reason='Bulk 404 check',
                    http_status=404
                )
                found_404 += 1

            if (i + 1) % 10 == 0:
                print(f"  Checked {i + 1}/{len(self.discovered_pages)}...")

        engine.close()
        print(f"✓ Found {found_404} pages with 404 errors")

    def _export_discovered(self):
        """Export discovered pages to file (URLS.txt format)."""
        filename = input("Output filename (default: discovered_pages.txt): ").strip()
        if not filename:
            filename = 'discovered_pages.txt'

        # Get approved pages or all discovered?
        choice = input("Export (a)ll or only (a)pproved pages? (a/p): ").strip().lower()

        if choice == 'p':
            pages_to_export = self.db.get_discovered_pages(status='approved')
        else:
            pages_to_export = self.db.get_discovered_pages(status='discovered')

        if not pages_to_export:
            print("No pages to export")
            return

        try:
            output_file = Path(filename)
            with output_file.open('w') as f:
                for i, page in enumerate(pages_to_export, 1):
                    page_id = page['target_page_id']
                    url = self._build_url(page_id)
                    f.write(f"{i}→{url}\n")

            print(f"✓ Exported {len(pages_to_export)} pages to {output_file}")
        except Exception as e:
            print(f"✗ Error: {e}")

    def _show_help(self):
        """Show help text."""
        print("""
Navigation:
  [a] - Approve this page for conversion
  [s] - Skip this page permanently
  [c] - Check if page exists on wiki (HTTP HEAD)
  [v] - View source pages linking to this page
  [n] - Next page
  [p] - Previous page
  [q] - Quit
  [b] - Show bulk operations menu
  [h] - Show this help

Bulk Operations:
  [1] - Approve all discovered pages
  [2] - Skip all discovered pages
  [3] - Approve by namespace pattern (e.g., 183_notes:examples:*)
  [4] - Approve pages with minimum reference count
  [5] - Check all pages for 404s
  [6] - Export to file (URLS.txt format)
        """)

    def _build_url(self, page_id: str) -> str:
        """Build wiki URL for a page ID."""
        base = self.wiki_url or 'https://wiki.example.com'
        return f"{base}/doku.php?id={page_id}"

    def close(self):
        """Close database connection."""
        self.db.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Entry point for discovery CLI."""
    import argparse

    parser = argparse.ArgumentParser(description='Review and manage discovered pages')
    parser.add_argument('--db', default='output/conversion_history.db', help='Database path')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    parser.add_argument('--export', help='Export to file (URLS.txt format)')
    parser.add_argument('--bulk-approve', action='store_true', help='Approve all discovered pages')
    parser.add_argument('--bulk-skip', action='store_true', help='Skip all discovered pages')

    args = parser.parse_args()

    with DiscoveryCLI(args.db) as cli:
        if args.stats:
            # Show statistics
            stats = cli.db.get_discovery_statistics()
            print("\nDiscovery Statistics:")
            print(f"  Discovered: {stats['discovered']}")
            print(f"  Approved: {stats['approved']}")
            print(f"  Skipped: {stats['skipped']}")
            print(f"  Failed 404: {stats['failed_404']}")
            print(f"  Converted: {stats['converted']}")
        elif args.export:
            # Export to file
            pages = cli.db.get_discovered_pages(status='discovered')
            with open(args.export, 'w') as f:
                for i, page in enumerate(pages, 1):
                    url = cli._build_url(page['target_page_id'])
                    f.write(f"{i}→{url}\n")
            print(f"✓ Exported {len(pages)} pages to {args.export}")
        elif args.bulk_approve:
            # Bulk approve
            pages = cli.db.get_discovered_pages(status='discovered')
            page_ids = [p['target_page_id'] for p in pages]
            cli.db.bulk_update_discovery_status(page_ids, 'approved', 'CLI bulk approve')
            print(f"✓ Approved {len(page_ids)} pages")
        elif args.bulk_skip:
            # Bulk skip
            pages = cli.db.get_discovered_pages(status='discovered')
            page_ids = [p['target_page_id'] for p in pages]
            cli.db.bulk_update_discovery_status(page_ids, 'skipped', 'CLI bulk skip')
            print(f"✓ Skipped {len(page_ids)} pages")
        else:
            # Interactive review
            cli.run()


if __name__ == '__main__':
    main()
