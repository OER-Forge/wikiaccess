#!/usr/bin/env python3
"""
Discovery Orchestration - Clean separation of discovery concerns

This module decouples discovery logic from the main conversion pipeline.
Previously discovery logic was mixed into unified.py (lines 598-623).

Now it's a clean, testable orchestrator that manages the discovery workflow:
- Auto-discovery from broken links
- Pagination and depth tracking
- Discovery reporting
- Manual review integration
"""

from typing import Dict, Any, Optional, List
from .database import ConversionDatabase
from .discovery import PageDiscoveryEngine


class DiscoveryOrchestrator:
    """Orchestrates the page discovery workflow.

    Manages auto-discovery of missing pages from broken links,
    depth tracking, and integration with the manual review process.

    Usage:
        >>> db = ConversionDatabase()
        >>> orchestrator = DiscoveryOrchestrator(db, 'https://wiki.example.com')
        >>> stats = orchestrator.discover_from_batch('batch_1', max_depth=2)
    """

    def __init__(self, db: ConversionDatabase, wiki_url: str,
                 max_discovery_depth: int = 2):
        """Initialize discovery orchestrator.

        Args:
            db: ConversionDatabase instance
            wiki_url: Base wiki URL for discovery
            max_discovery_depth: Maximum discovery depth to prevent infinite loops
        """
        self.db = db
        self.wiki_url = wiki_url
        self.max_discovery_depth = max_discovery_depth
        self.discovery_engine = PageDiscoveryEngine(db, wiki_url, max_discovery_depth)

    def run_auto_discovery(self, batch_id: str, verbose: bool = True) -> Dict[str, Any]:
        """Run auto-discovery for a batch.

        This is the main entry point for discovering new pages from broken links.
        It respects the max_depth limit to prevent infinite discovery loops.

        Args:
            batch_id: Batch identifier
            verbose: Whether to print progress

        Returns:
            Discovery statistics dict
        """
        if verbose:
            print(f"\n{'='*70}\nAuto-Discovery Process\n{'='*70}")

        # Get batch info
        batch_info = self.db.get_batch_info(batch_id)
        if not batch_info:
            if verbose:
                print(f"Batch {batch_id} not found")
            return {'error': 'Batch not found'}

        current_depth = batch_info.get('discovery_depth', 0)

        # Check depth limit
        if current_depth >= self.max_discovery_depth:
            if verbose:
                print(f"Reached max discovery depth ({self.max_discovery_depth})")
            return {
                'new_discoveries': 0,
                'already_known': 0,
                'external_links': 0,
                'depth_limit_reached': True
            }

        # Run discovery
        if verbose:
            print(f"Current depth: {current_depth}")
            print(f"Max depth: {self.max_discovery_depth}")

        discovery_stats = self.discovery_engine.discover_from_batch(batch_id, current_depth)

        if verbose:
            self._print_discovery_summary(discovery_stats, current_depth)

        return discovery_stats

    def get_discovery_status(self) -> Dict[str, Any]:
        """Get overall discovery status using database abstraction.

        Returns:
            Dict with discovery statistics across all batches
        """
        return self.db.get_discovery_status_counts()

    def approve_pages_by_namespace(self, namespace_pattern: str) -> int:
        """Approve all discovered pages matching a namespace pattern.

        Args:
            namespace_pattern: Pattern like '183_notes:examples:*'

        Returns:
            Number of pages approved
        """
        return self.db.approve_discovered_by_namespace(namespace_pattern)

    def approve_pages_by_depth(self, depth: int) -> int:
        """Approve all discovered pages at a specific depth.

        Args:
            depth: Discovery depth to approve

        Returns:
            Number of pages approved
        """
        return self.db.approve_discovered_by_depth(depth)

    def skip_broken_links(self, max_reference_count: int = 1) -> int:
        """Mark low-reference broken links as 'skipped' to avoid noise.

        Args:
            max_reference_count: Skip pages referenced <= this many times

        Returns:
            Number of pages skipped
        """
        return self.db.skip_low_reference_pages(max_reference_count)

    def get_pages_pending_review(self) -> List[Dict[str, Any]]:
        """Get all pages awaiting manual review.

        Returns:
            List of discovered pages awaiting approval
        """
        return self.db.get_pending_discovery_pages()

    def get_pages_ready_to_convert(self) -> List[str]:
        """Get all pages approved and ready for conversion.

        Returns:
            List of approved page IDs
        """
        return self.db.get_approved_for_conversion()

    def get_discovery_progress(self) -> Dict[str, Any]:
        """Get detailed discovery progress statistics.

        Returns:
            Dict with progress information
        """
        progress = self.db.get_discovery_progress()
        progress['next_action'] = self._recommend_next_action(progress.get('by_status', {}))
        return progress

    def close(self) -> None:
        """Clean up discovery resources."""
        self.discovery_engine.close()

    @staticmethod
    def _print_discovery_summary(stats: Dict[str, Any], depth: int) -> None:
        """Print human-readable discovery summary.

        Args:
            stats: Discovery statistics
            depth: Current discovery depth
        """
        print(f"\nDiscovery Results (Depth {depth}):")
        print(f"  New discoveries: {stats.get('new_discoveries', 0)}")
        print(f"  Already known: {stats.get('already_known', 0)}")
        print(f"  External links: {stats.get('external_links', 0)}")

        if stats.get('new_discoveries', 0) > 0:
            print(f"\n📋 Review with: python review_discoveries.py")

    @staticmethod
    def _recommend_next_action(status_counts: Dict[str, int]) -> str:
        """Recommend next action based on discovery status.

        Args:
            status_counts: Dict of status counts

        Returns:
            Recommended action string
        """
        discovered = status_counts.get('discovered', 0)
        approved = status_counts.get('approved', 0)

        if discovered > 0 and approved == 0:
            return 'Run: python review_discoveries.py'
        elif approved > 0:
            return 'Run: python convert_approved.py'
        else:
            return 'Run initial conversion: python convert_from_file_list.py'
