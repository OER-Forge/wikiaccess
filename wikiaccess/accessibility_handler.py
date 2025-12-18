#!/usr/bin/env python3
"""
Centralized Accessibility Issue Handling

This module provides a single point for storing accessibility issues,
eliminating duplication across convert_wiki_page and convert_multiple_pages.

Previously this logic was duplicated in 2 places (40+ lines each).
Now it's a single reusable handler.
"""

from typing import Any, Dict, List
from .database import ConversionDatabase


class AccessibilityIssueHandler:
    """Handles storage of accessibility issues for pages."""

    @staticmethod
    def store_issues(db: ConversionDatabase, page_id: str, batch_id: str,
                     accessibility_results: Dict[str, Any]) -> None:
        """Store accessibility issues for a page.

        This is the single point where accessibility issues are recorded,
        whether they come from single-page or batch conversions.

        Args:
            db: ConversionDatabase instance
            page_id: Page identifier
            batch_id: Batch identifier
            accessibility_results: Dict with 'html' and 'docx' keys containing:
                - score_aa: AA compliance score (0-100)
                - score_aaa: AAA compliance score (0-100)
                - issues_aa: List of AA level issues
                - issues_aaa: List of AAA level issues
                - warnings: Optional list of warnings

        Example:
            >>> db = ConversionDatabase()
            >>> results = {
            ...     'html': {
            ...         'score_aa': 95,
            ...         'score_aaa': 80,
            ...         'issues_aa': [...],
            ...         'issues_aaa': [...]
            ...     },
            ...     'docx': {...}
            ... }
            >>> AccessibilityIssueHandler.store_issues(db, 'page_id', 'batch_1', results)
        """
        db.store_page_accessibility_issues(page_id, batch_id, accessibility_results)

    @staticmethod
    def update_page_scores(db: ConversionDatabase, page_id: str,
                           accessibility_results: Dict[str, Any]) -> None:
        """Update accessibility scores for a page in the database.

        Args:
            db: ConversionDatabase instance
            page_id: Page identifier
            accessibility_results: Dict with 'html' and 'docx' keys
        """
        html_aa = accessibility_results.get('html', {}).get('score_aa', 0)
        html_aaa = accessibility_results.get('html', {}).get('score_aaa', 0)
        docx_aa = accessibility_results.get('docx', {}).get('score_aa', 0)
        docx_aaa = accessibility_results.get('docx', {}).get('score_aaa', 0)

        db.update_page_accessibility_scores(page_id, html_aa, html_aaa, docx_aa, docx_aaa)

    @staticmethod
    def store_and_update(db: ConversionDatabase, page_id: str, batch_id: str,
                         accessibility_results: Dict[str, Any]) -> None:
        """Store issues and update page scores in one call.

        This is a convenience method to do both operations atomically.

        Args:
            db: ConversionDatabase instance
            page_id: Page identifier
            batch_id: Batch identifier
            accessibility_results: Accessibility check results
        """
        AccessibilityIssueHandler.store_issues(db, page_id, batch_id, accessibility_results)
        AccessibilityIssueHandler.update_page_scores(db, page_id, accessibility_results)

    @staticmethod
    def get_page_accessibility_summary(db: ConversionDatabase, page_id: str) -> Dict[str, Any]:
        """Get accessibility summary for a page.

        Args:
            db: ConversionDatabase instance
            page_id: Page identifier

        Returns:
            Dict with scores and issue counts
        """
        return db.get_page_accessibility_summary(page_id)
