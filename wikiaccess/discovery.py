"""
Page Discovery Engine for WikiAccess

This module handles discovering missing pages from broken links,
tracking their status, and managing the discovery workflow.
"""

import requests
from typing import Optional, Dict, List, Any, Set, Tuple
from pathlib import Path
import logging
from datetime import datetime

from .database import ConversionDatabase

logger = logging.getLogger(__name__)


class PageDiscoveryEngine:
    """
    Discovers new pages from broken links and manages discovery state.

    Features:
    - Discovers missing pages referenced in broken links
    - Checks page availability via HTTP HEAD requests
    - Tracks discovery depth to prevent infinite loops
    - Deduplicates against already converted/discovered pages
    - Manages discovery status workflow
    """

    def __init__(self, db: ConversionDatabase, wiki_url: str, max_depth: int = 2):
        """
        Initialize the discovery engine.

        Args:
            db: Database connection for tracking discoveries
            wiki_url: Base URL of the wiki (e.g., 'https://wiki.example.com')
            max_depth: Maximum discovery depth (0 = original URLS.txt, 1+ = discovered)
        """
        self.db = db
        self.wiki_url = wiki_url.rstrip('/')
        self.max_depth = max_depth
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikiAccess-Discovery/1.0'
        })
        # Cache for page existence checks (page_id -> (exists, http_status))
        self._existence_cache: Dict[str, Tuple[bool, int]] = {}

    def discover_from_batch(self, batch_id: str, current_depth: int = 0) -> Dict[str, Any]:
        """
        Analyze broken links from a batch and discover new pages.

        Args:
            batch_id: Batch ID to analyze for broken links
            current_depth: Current discovery depth (for loop prevention)

        Returns:
            Dictionary with discovery statistics
        """
        logger.info(f"Starting discovery from batch {batch_id} at depth {current_depth}")

        stats = {
            'total_broken_links': 0,
            'new_discoveries': 0,
            'already_known': 0,
            'failed_404_count': 0,
            'external_links': 0,
            'skipped_depth': 0,
        }

        # Check depth limit
        if current_depth >= self.max_depth:
            logger.info(f"Reached max depth {self.max_depth}, skipping discovery")
            stats['skipped_depth'] = 1
            return stats

        # Get all broken links from this batch
        broken_links = self.db.get_broken_links(batch_id)

        if not broken_links:
            logger.info("No broken links found in batch")
            return stats

        logger.info(f"Found {len(broken_links)} broken links to analyze")
        stats['total_broken_links'] = len(broken_links)

        # Get already converted pages to avoid rediscovering
        converted_pages = self.db.get_all_page_ids(batch_id)

        for link_data in broken_links:
            target_page_id = link_data['target_page_id']
            reference_count = link_data.get('reference_count', 1)
            referenced_by = link_data.get('referenced_by', '').split(',') if link_data.get('referenced_by') else []

            # Skip if already converted in this batch
            if target_page_id in converted_pages:
                logger.debug(f"Skipping {target_page_id} (already converted in batch)")
                stats['already_known'] += 1
                continue

            # Check if already discovered
            existing = self.db.is_page_discovered(target_page_id)
            if existing:
                logger.debug(f"Page already discovered: {target_page_id} (status: {existing['discovery_status']})")
                # Increment reference count if still discovering
                if existing['discovery_status'] == 'discovered':
                    self.db.increment_discovery_reference_count(target_page_id)
                stats['already_known'] += 1
                continue

            # Record new discovery
            discovery_id = self.db.add_discovered_page({
                'target_page_id': target_page_id,
                'wiki_url': self.wiki_url,
                'discovery_depth': current_depth + 1,
                'discovery_status': 'discovered',
                'first_discovered_by_batch': batch_id,
                'reference_count': reference_count,
            })

            if discovery_id:
                logger.info(f"Discovered new page: {target_page_id} (depth {current_depth + 1}, {reference_count} refs)")
                stats['new_discoveries'] += 1

                # Record source pages
                for source_page_id in referenced_by:
                    source_page_id = source_page_id.strip()
                    if source_page_id:
                        self.db.add_discovery_source({
                            'discovered_page_id': discovery_id,
                            'source_page_id': source_page_id,
                            'batch_id': batch_id,
                        })

        logger.info(
            f"Discovery complete: {stats['new_discoveries']} new, "
            f"{stats['already_known']} already known, "
            f"{stats['failed_404_count']} 404s"
        )
        return stats

    def check_page_exists(self, page_id: str) -> Tuple[bool, int]:
        """
        Check if a page exists on the wiki via HTTP HEAD request.

        Args:
            page_id: DokuWiki page ID (e.g., '183_notes:momentum')

        Returns:
            Tuple of (exists: bool, http_status_code: int)
        """
        # Check cache first
        if page_id in self._existence_cache:
            return self._existence_cache[page_id]

        try:
            # Build URL for the page
            url = self._build_page_url(page_id)

            # Make HEAD request to check existence
            response = self.session.head(url, timeout=5, allow_redirects=True)
            http_status = response.status_code

            # Cache result
            exists = http_status == 200
            self._existence_cache[page_id] = (exists, http_status)

            logger.debug(f"Page {page_id}: HTTP {http_status}")

            # Record in database if 404
            if http_status == 404:
                self.db.check_page_http_status(page_id, http_status)

            return exists, http_status

        except requests.Timeout:
            logger.warning(f"Timeout checking page {page_id}")
            return False, 0
        except requests.RequestException as e:
            logger.warning(f"Error checking page {page_id}: {e}")
            return False, 0

    def check_all_discovered_pages(self) -> Dict[str, Any]:
        """
        Check HTTP status for all discovered pages.

        Returns:
            Dictionary with check statistics
        """
        logger.info("Checking HTTP status for all discovered pages")

        discovered = self.db.get_discovered_pages(status='discovered')
        stats = {
            'total_checked': len(discovered),
            'found': 0,
            'not_found': 0,
            'errors': 0,
        }

        for page_data in discovered:
            page_id = page_data['target_page_id']
            exists, status = self.check_page_exists(page_id)

            if status == 200:
                stats['found'] += 1
            elif status == 404:
                stats['not_found'] += 1
                # Auto-update status
                self.db.update_discovery_status(
                    page_id, 'failed_404',
                    reason='HTTP 404 - Page not found',
                    http_status=404
                )
            else:
                stats['errors'] += 1

        logger.info(
            f"Checked {stats['total_checked']}: "
            f"{stats['found']} found, "
            f"{stats['not_found']} 404s, "
            f"{stats['errors']} errors"
        )
        return stats

    def _build_page_url(self, page_id: str) -> str:
        """
        Build the DokuWiki URL for a page.

        Args:
            page_id: DokuWiki page ID (e.g., '183_notes:momentum')

        Returns:
            Full URL to the page
        """
        return f"{self.wiki_url}/doku.php?id={page_id}"

    def auto_discover_after_conversion(self, batch_id: str) -> Optional[Path]:
        """
        Automatically trigger discovery after batch completion.

        Called after convert_multiple_pages() finishes.

        Args:
            batch_id: Batch ID that just completed

        Returns:
            Path to discovery report HTML if discoveries found, None otherwise
        """
        logger.info(f"Auto-triggering discovery after batch {batch_id}")

        # Get batch info
        batch_info = self.db.get_batch_info(batch_id)
        if not batch_info:
            logger.warning(f"Batch {batch_id} not found")
            return None

        current_depth = batch_info.get('discovery_depth', 0)

        # Run discovery
        stats = self.discover_from_batch(batch_id, current_depth)

        # Update batch with discovery stats
        if stats['new_discoveries'] > 0:
            self.db.conn.execute("""
                UPDATE conversion_batches
                SET pages_discovered_count = ?,
                    discovery_enabled = 1
                WHERE batch_id = ?
            """, (stats['new_discoveries'], batch_id))
            self.db.conn.commit()

            logger.info(
                f"Auto-discovery complete: {stats['new_discoveries']} new pages discovered"
            )
            return Path('discovery_report.html')  # Will be generated by reporting module

        logger.info("No new pages discovered")
        return None

    def get_discovery_summary(self) -> Dict[str, Any]:
        """
        Get summary of discovered pages.

        Returns:
            Dictionary with discovery statistics
        """
        stats = self.db.get_discovery_statistics()

        discovered_pages = self.db.get_discovered_pages(status='discovered')
        approved_pages = self.db.get_discovered_pages(status='approved')

        total_references = sum(page.get('reference_count', 0) for page in discovered_pages)
        avg_references = total_references / len(discovered_pages) if discovered_pages else 0

        return {
            'statistics': stats,
            'discovered_count': len(discovered_pages),
            'approved_count': len(approved_pages),
            'total_references': total_references,
            'avg_references_per_page': round(avg_references, 1),
            'most_referenced': discovered_pages[0] if discovered_pages else None,
        }

    def close(self):
        """Close HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
