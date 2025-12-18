"""
SQLite database layer for WikiAccess conversion tracking.

This module provides persistent storage for:
- Page conversion history and metadata
- Image download tracking
- Accessibility scores and issues
- Link tracking and broken link detection
- Batch processing state
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import contextlib


class ConversionDatabase:
    """Manages SQLite database for conversion tracking."""

    def __init__(self, db_path: str = "output/conversion_history.db"):
        """Initialize database connection and create schema if needed.

        Args:
            db_path: Path to SQLite database file. Defaults to output/conversion_history.db
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()
        self._create_schema()

    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")

    def _create_schema(self):
        """Create database schema if it doesn't exist."""
        with self.conn:
            # Conversion batches table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS conversion_batches (
                    batch_id TEXT PRIMARY KEY,
                    wiki_url TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_pages INTEGER DEFAULT 0,
                    successful_pages INTEGER DEFAULT 0,
                    failed_pages INTEGER DEFAULT 0,
                    total_images INTEGER DEFAULT 0,
                    failed_images INTEGER DEFAULT 0
                )
            """)

            # Pages table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wiki_url TEXT NOT NULL,
                    page_id TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    conversion_status TEXT NOT NULL CHECK(conversion_status IN ('SUCCESS', 'FAILED', 'PARTIAL')),
                    markdown_path TEXT,
                    html_path TEXT,
                    docx_path TEXT,
                    html_wcag_aa_score INTEGER,
                    html_wcag_aaa_score INTEGER,
                    docx_wcag_aa_score INTEGER,
                    docx_wcag_aaa_score INTEGER,
                    image_count INTEGER DEFAULT 0,
                    image_success_count INTEGER DEFAULT 0,
                    image_failed_count INTEGER DEFAULT 0,
                    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    conversion_duration_seconds REAL,
                    error_message TEXT,
                    FOREIGN KEY(batch_id) REFERENCES conversion_batches(batch_id)
                )
            """)

            # Create index for efficient queries
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pages_lookup
                ON pages(wiki_url, page_id, converted_at DESC)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pages_batch
                ON pages(batch_id, conversion_status)
            """)

            # Images table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('wiki_image', 'youtube_thumbnail', 'external_url')),
                    source_url TEXT NOT NULL,
                    local_filename TEXT,
                    status TEXT NOT NULL CHECK(status IN ('success', 'failed', 'cached', 'skipped', 'error', 'pending')),
                    file_size INTEGER,
                    dimensions TEXT,
                    alt_text TEXT,
                    alt_text_quality TEXT CHECK(alt_text_quality IN ('missing', 'auto_generated', 'manual')),
                    error_message TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_images_page
                ON images(page_id, batch_id)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_images_status
                ON images(status, source_url)
            """)

            # Links table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_page_id TEXT NOT NULL,
                    target_page_id TEXT NOT NULL,
                    link_text TEXT,
                    link_type TEXT CHECK(link_type IN ('internal', 'external', 'anchor')),
                    resolution_status TEXT CHECK(resolution_status IN ('found', 'missing', 'external')),
                    batch_id TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_links_source
                ON links(source_page_id, batch_id)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_links_target
                ON links(target_page_id, resolution_status)
            """)

            # Accessibility issues table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS accessibility_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    format TEXT NOT NULL CHECK(format IN ('HTML', 'DOCX')),
                    level TEXT NOT NULL CHECK(level IN ('AA', 'AAA')),
                    issue_code TEXT NOT NULL,
                    issue_message TEXT,
                    element_selector TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_accessibility_page
                ON accessibility_issues(page_id, batch_id)
            """)

            # Discovered pages table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS discovered_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_page_id TEXT NOT NULL UNIQUE,
                    wiki_url TEXT NOT NULL,
                    discovery_depth INTEGER NOT NULL DEFAULT 1,
                    discovery_status TEXT NOT NULL CHECK(
                        discovery_status IN ('discovered', 'approved', 'skipped', 'failed_404', 'converted')
                    ),
                    first_discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    first_discovered_by_batch TEXT,
                    reference_count INTEGER DEFAULT 0,
                    decision_made_at TIMESTAMP,
                    decision_reason TEXT,
                    converted_at TIMESTAMP,
                    converted_batch_id TEXT,
                    http_status_code INTEGER,
                    last_check_at TIMESTAMP,
                    check_attempt_count INTEGER DEFAULT 0,
                    FOREIGN KEY(first_discovered_by_batch) REFERENCES conversion_batches(batch_id),
                    FOREIGN KEY(converted_batch_id) REFERENCES conversion_batches(batch_id)
                )
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discovered_status
                ON discovered_pages(discovery_status, discovery_depth)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discovered_page_id
                ON discovered_pages(target_page_id)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discovered_batch
                ON discovered_pages(first_discovered_by_batch)
            """)

            # Discovery sources table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS discovery_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discovered_page_id INTEGER NOT NULL,
                    source_page_id TEXT NOT NULL,
                    link_text TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_id TEXT NOT NULL,
                    FOREIGN KEY(discovered_page_id) REFERENCES discovered_pages(id),
                    FOREIGN KEY(batch_id) REFERENCES conversion_batches(batch_id)
                )
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discovery_sources_page
                ON discovery_sources(discovered_page_id)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_discovery_sources_batch
                ON discovery_sources(batch_id)
            """)

            # Add discovery columns to existing tables if needed
            try:
                self.conn.execute("ALTER TABLE conversion_batches ADD COLUMN discovery_enabled BOOLEAN DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                self.conn.execute("ALTER TABLE conversion_batches ADD COLUMN pages_discovered_count INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass

            try:
                self.conn.execute("ALTER TABLE conversion_batches ADD COLUMN parent_batch_id TEXT")
            except sqlite3.OperationalError:
                pass

            try:
                self.conn.execute("ALTER TABLE conversion_batches ADD COLUMN discovery_depth INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass

            try:
                self.conn.execute("ALTER TABLE pages ADD COLUMN discovery_depth INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass

    @contextlib.contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    # Batch operations

    def start_batch(self, batch_id: str, wiki_url: str) -> None:
        """Record the start of a conversion batch.

        Args:
            batch_id: Unique identifier for this batch
            wiki_url: Base URL of the wiki being converted
        """
        with self.transaction():
            self.conn.execute("""
                INSERT INTO conversion_batches (batch_id, wiki_url)
                VALUES (?, ?)
            """, (batch_id, wiki_url))

    def complete_batch(self, batch_id: str, stats: Dict[str, int]) -> None:
        """Record batch completion with statistics.

        Args:
            batch_id: Batch identifier
            stats: Dictionary with total_pages, successful_pages, failed_pages,
                   total_images, failed_images
        """
        with self.transaction():
            self.conn.execute("""
                UPDATE conversion_batches
                SET completed_at = CURRENT_TIMESTAMP,
                    total_pages = ?,
                    successful_pages = ?,
                    failed_pages = ?,
                    total_images = ?,
                    failed_images = ?
                WHERE batch_id = ?
            """, (
                stats.get('total_pages', 0),
                stats.get('successful_pages', 0),
                stats.get('failed_pages', 0),
                stats.get('total_images', 0),
                stats.get('failed_images', 0),
                batch_id
            ))

    def get_batch_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Dictionary with batch information or None if not found
        """
        cursor = self.conn.execute("""
            SELECT * FROM conversion_batches WHERE batch_id = ?
        """, (batch_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # Page operations

    def add_page_conversion(self, page_data: Dict[str, Any]) -> int:
        """Record a page conversion.

        Args:
            page_data: Dictionary with page conversion details

        Returns:
            Row ID of inserted page record
        """
        with self.transaction():
            cursor = self.conn.execute("""
                INSERT INTO pages (
                    wiki_url, page_id, batch_id, conversion_status,
                    markdown_path, html_path, docx_path,
                    html_wcag_aa_score, html_wcag_aaa_score,
                    docx_wcag_aa_score, docx_wcag_aaa_score,
                    image_count, image_success_count, image_failed_count,
                    conversion_duration_seconds, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                page_data.get('wiki_url'),
                page_data.get('page_id'),
                page_data.get('batch_id'),
                page_data.get('conversion_status', 'SUCCESS'),
                page_data.get('markdown_path'),
                page_data.get('html_path'),
                page_data.get('docx_path'),
                page_data.get('html_wcag_aa_score'),
                page_data.get('html_wcag_aaa_score'),
                page_data.get('docx_wcag_aa_score'),
                page_data.get('docx_wcag_aaa_score'),
                page_data.get('image_count', 0),
                page_data.get('image_success_count', 0),
                page_data.get('image_failed_count', 0),
                page_data.get('conversion_duration_seconds'),
                page_data.get('error_message')
            ))
            return cursor.lastrowid

    def get_page_history(self, wiki_url: str, page_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversion history for a specific page.

        Args:
            wiki_url: Wiki base URL
            page_id: Page identifier
            limit: Maximum number of records to return

        Returns:
            List of conversion records, newest first
        """
        cursor = self.conn.execute("""
            SELECT * FROM pages
            WHERE wiki_url = ? AND page_id = ?
            ORDER BY converted_at DESC
            LIMIT ?
        """, (wiki_url, page_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def was_recently_converted(self, wiki_url: str, page_id: str, hours: int = 1) -> bool:
        """Check if a page was successfully converted recently.

        Args:
            wiki_url: Wiki base URL
            page_id: Page identifier
            hours: Time window in hours

        Returns:
            True if page was converted successfully within the time window
        """
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM pages
            WHERE wiki_url = ? AND page_id = ?
            AND conversion_status = 'SUCCESS'
            AND converted_at > datetime('now', '-' || ? || ' hours')
        """, (wiki_url, page_id, hours))
        return cursor.fetchone()[0] > 0

    def get_failed_pages(self, batch_id: str) -> List[str]:
        """Get list of page IDs that failed conversion in a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            List of page IDs that failed
        """
        cursor = self.conn.execute("""
            SELECT page_id FROM pages
            WHERE batch_id = ? AND conversion_status = 'FAILED'
        """, (batch_id,))
        return [row[0] for row in cursor.fetchall()]

    def get_converted_pages(self, batch_id: str) -> List[str]:
        """Get list of successfully converted page IDs in a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            List of page IDs that were successfully converted
        """
        cursor = self.conn.execute("""
            SELECT page_id FROM pages
            WHERE batch_id = ? AND conversion_status = 'SUCCESS'
        """, (batch_id,))
        return [row[0] for row in cursor.fetchall()]

    # Image operations

    def add_image(self, image_data: Dict[str, Any]) -> int:
        """Record an image download attempt.

        Args:
            image_data: Dictionary with image details

        Returns:
            Row ID of inserted image record
        """
        with self.transaction():
            cursor = self.conn.execute("""
                INSERT INTO images (
                    page_id, batch_id, type, source_url, local_filename,
                    status, file_size, dimensions, alt_text, alt_text_quality,
                    error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                image_data.get('page_id'),
                image_data.get('batch_id'),
                image_data.get('type'),
                image_data.get('source_url'),
                image_data.get('local_filename'),
                image_data.get('status'),
                image_data.get('file_size'),
                image_data.get('dimensions'),
                image_data.get('alt_text'),
                image_data.get('alt_text_quality'),
                image_data.get('error_message')
            ))
            return cursor.lastrowid

    def get_failed_images(self, batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of images that failed to download.

        Args:
            batch_id: Optional batch ID to filter by

        Returns:
            List of failed image records
        """
        if batch_id:
            cursor = self.conn.execute("""
                SELECT * FROM images
                WHERE batch_id = ? AND status = 'failed'
                ORDER BY page_id, source_url
            """, (batch_id,))
        else:
            cursor = self.conn.execute("""
                SELECT * FROM images
                WHERE status = 'failed'
                ORDER BY downloaded_at DESC
            """)
        return [dict(row) for row in cursor.fetchall()]

    def get_image_failure_stats(self) -> List[Dict[str, Any]]:
        """Get statistics on image download failures by source URL.

        Returns:
            List of dicts with source_url, failure_count, total_attempts, failure_rate
        """
        cursor = self.conn.execute("""
            SELECT
                source_url,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failure_count,
                COUNT(*) as total_attempts,
                ROUND(100.0 * SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) / COUNT(*), 1) as failure_rate
            FROM images
            GROUP BY source_url
            HAVING failure_count > 0
            ORDER BY failure_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    # Link operations

    def add_link(self, link_data: Dict[str, Any]) -> int:
        """Record a link found in a page.

        Args:
            link_data: Dictionary with link details

        Returns:
            Row ID of inserted link record
        """
        with self.transaction():
            cursor = self.conn.execute("""
                INSERT INTO links (
                    source_page_id, target_page_id, link_text,
                    link_type, resolution_status, batch_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                link_data.get('source_page_id'),
                link_data.get('target_page_id'),
                link_data.get('link_text'),
                link_data.get('link_type'),
                link_data.get('resolution_status'),
                link_data.get('batch_id')
            ))
            return cursor.lastrowid

    def get_broken_links(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all broken (missing) internal links for a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            List of broken link records
        """
        cursor = self.conn.execute("""
            SELECT
                target_page_id,
                COUNT(*) as reference_count,
                GROUP_CONCAT(DISTINCT source_page_id) as referenced_by
            FROM links
            WHERE batch_id = ?
            AND link_type = 'internal'
            AND resolution_status = 'missing'
            GROUP BY target_page_id
            ORDER BY reference_count DESC
        """, (batch_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_page_links(self, page_id: str, batch_id: str) -> List[Dict[str, Any]]:
        """Get all links from a specific page.

        Args:
            page_id: Source page identifier
            batch_id: Batch identifier

        Returns:
            List of link records
        """
        cursor = self.conn.execute("""
            SELECT * FROM links
            WHERE source_page_id = ? AND batch_id = ?
            ORDER BY link_type, target_page_id
        """, (page_id, batch_id))
        return [dict(row) for row in cursor.fetchall()]

    # Accessibility operations

    def add_accessibility_issue(self, issue_data: Dict[str, Any]) -> int:
        """Record an accessibility issue.

        Args:
            issue_data: Dictionary with issue details

        Returns:
            Row ID of inserted issue record
        """
        with self.transaction():
            cursor = self.conn.execute("""
                INSERT INTO accessibility_issues (
                    page_id, batch_id, format, level,
                    issue_code, issue_message, element_selector
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_data.get('page_id'),
                issue_data.get('batch_id'),
                issue_data.get('format'),
                issue_data.get('level'),
                issue_data.get('issue_code'),
                issue_data.get('issue_message'),
                issue_data.get('element_selector')
            ))
            return cursor.lastrowid

    def get_accessibility_trends(self, wiki_url: str, page_id: str) -> List[Dict[str, Any]]:
        """Get accessibility score trends for a page over time.

        Args:
            wiki_url: Wiki base URL
            page_id: Page identifier

        Returns:
            List of records with scores and dates
        """
        cursor = self.conn.execute("""
            SELECT
                converted_at,
                html_wcag_aa_score,
                html_wcag_aaa_score,
                docx_wcag_aa_score,
                docx_wcag_aaa_score
            FROM pages
            WHERE wiki_url = ? AND page_id = ?
            ORDER BY converted_at ASC
        """, (wiki_url, page_id))
        return [dict(row) for row in cursor.fetchall()]

    # Discovery operations

    def add_discovered_page(self, page_data: Dict[str, Any]) -> int:
        """Record a newly discovered page.

        Args:
            page_data: Dictionary with discovered page details
                Required: target_page_id, wiki_url, discovery_depth, discovery_status
                Optional: first_discovered_by_batch, reference_count, decision_reason

        Returns:
            Row ID of inserted record
        """
        with self.transaction():
            cursor = self.conn.execute("""
                INSERT OR IGNORE INTO discovered_pages (
                    target_page_id, wiki_url, discovery_depth, discovery_status,
                    first_discovered_by_batch, reference_count
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                page_data.get('target_page_id'),
                page_data.get('wiki_url'),
                page_data.get('discovery_depth', 1),
                page_data.get('discovery_status', 'discovered'),
                page_data.get('first_discovered_by_batch'),
                page_data.get('reference_count', 1)
            ))
            return cursor.lastrowid

    def add_discovery_source(self, source_data: Dict[str, Any]) -> int:
        """Record a source page for a discovered page.

        Args:
            source_data: Dictionary with discovery source details
                Required: discovered_page_id, source_page_id, batch_id
                Optional: link_text

        Returns:
            Row ID of inserted record
        """
        with self.transaction():
            cursor = self.conn.execute("""
                INSERT INTO discovery_sources (
                    discovered_page_id, source_page_id, link_text, batch_id
                ) VALUES (?, ?, ?, ?)
            """, (
                source_data.get('discovered_page_id'),
                source_data.get('source_page_id'),
                source_data.get('link_text'),
                source_data.get('batch_id')
            ))
            return cursor.lastrowid

    def get_discovered_pages(self, status: Optional[str] = None,
                            depth: Optional[int] = None,
                            wiki_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get discovered pages with optional filtering.

        Args:
            status: Filter by discovery_status (discovered, approved, skipped, failed_404, converted)
            depth: Filter by discovery_depth
            wiki_url: Filter by wiki_url

        Returns:
            List of discovered page records
        """
        query = "SELECT * FROM discovered_pages WHERE 1=1"
        params = []

        if status:
            query += " AND discovery_status = ?"
            params.append(status)
        if depth is not None:
            query += " AND discovery_depth = ?"
            params.append(depth)
        if wiki_url:
            query += " AND wiki_url = ?"
            params.append(wiki_url)

        query += " ORDER BY reference_count DESC, first_discovered_at ASC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def is_page_discovered(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Check if a page has been discovered.

        Args:
            page_id: Target page identifier

        Returns:
            Dictionary with page data if discovered, None otherwise
        """
        cursor = self.conn.execute("""
            SELECT * FROM discovered_pages WHERE target_page_id = ?
        """, (page_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_discovery_status(self, page_id: str, new_status: str,
                               reason: Optional[str] = None,
                               http_status: Optional[int] = None) -> None:
        """Update the status of a discovered page.

        Args:
            page_id: Target page identifier
            new_status: New discovery status
            reason: Optional reason for the status change
            http_status: Optional HTTP status code (for 404 tracking)
        """
        with self.transaction():
            updates = ["discovery_status = ?", "decision_made_at = CURRENT_TIMESTAMP"]
            params = [new_status]

            if reason:
                updates.append("decision_reason = ?")
                params.append(reason)

            if http_status:
                updates.append("http_status_code = ?")
                params.append(http_status)

            if new_status == 'converted':
                updates.append("converted_at = CURRENT_TIMESTAMP")

            params.append(page_id)

            query = f"UPDATE discovered_pages SET {', '.join(updates)} WHERE target_page_id = ?"
            self.conn.execute(query, params)

    def mark_discovered_as_converted(self, page_id: str, batch_id: str) -> None:
        """Mark a discovered page as successfully converted.

        Args:
            page_id: Page identifier
            batch_id: Batch identifier where conversion occurred
        """
        with self.transaction():
            self.conn.execute("""
                UPDATE discovered_pages
                SET discovery_status = 'converted',
                    converted_at = CURRENT_TIMESTAMP,
                    converted_batch_id = ?
                WHERE target_page_id = ?
            """, (batch_id, page_id))

    def get_discovery_sources(self, discovered_page_id: int) -> List[Dict[str, Any]]:
        """Get all source pages for a discovered page.

        Args:
            discovered_page_id: Row ID from discovered_pages table

        Returns:
            List of discovery source records
        """
        cursor = self.conn.execute("""
            SELECT * FROM discovery_sources
            WHERE discovered_page_id = ?
            ORDER BY discovered_at DESC
        """, (discovered_page_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_approved_pages_for_conversion(self, max_depth: Optional[int] = None) -> List[str]:
        """Get list of approved page IDs ready for conversion.

        Args:
            max_depth: Optional maximum discovery depth to include

        Returns:
            List of page IDs with status='approved'
        """
        query = "SELECT target_page_id FROM discovered_pages WHERE discovery_status = 'approved'"
        params = []

        if max_depth is not None:
            query += " AND discovery_depth <= ?"
            params.append(max_depth)

        query += " ORDER BY reference_count DESC"

        cursor = self.conn.execute(query, params)
        return [row[0] for row in cursor.fetchall()]

    def get_discovery_statistics(self) -> Dict[str, int]:
        """Get counts for each discovery status.

        Returns:
            Dictionary with status counts
        """
        cursor = self.conn.execute("""
            SELECT
                discovery_status,
                COUNT(*) as count
            FROM discovered_pages
            GROUP BY discovery_status
        """)
        stats = {row['discovery_status']: row['count'] for row in cursor.fetchall()}
        # Ensure all statuses are present
        for status in ['discovered', 'approved', 'skipped', 'failed_404', 'converted']:
            stats.setdefault(status, 0)
        return stats

    def increment_discovery_reference_count(self, page_id: str) -> None:
        """Increment the reference count for a discovered page.

        Args:
            page_id: Target page identifier
        """
        with self.transaction():
            self.conn.execute("""
                UPDATE discovered_pages
                SET reference_count = reference_count + 1
                WHERE target_page_id = ?
            """, (page_id,))

    def bulk_update_discovery_status(self, page_ids: List[str], new_status: str,
                                    reason: Optional[str] = None) -> int:
        """Bulk update status for multiple discovered pages.

        Args:
            page_ids: List of page IDs to update
            new_status: New discovery status
            reason: Optional reason for the status change

        Returns:
            Number of pages updated
        """
        if not page_ids:
            return 0

        with self.transaction():
            placeholders = ','.join('?' * len(page_ids))
            params = [new_status]

            if reason:
                query = f"""
                    UPDATE discovered_pages
                    SET discovery_status = ?,
                        decision_made_at = CURRENT_TIMESTAMP,
                        decision_reason = ?
                    WHERE target_page_id IN ({placeholders})
                """
                params.append(reason)
            else:
                query = f"""
                    UPDATE discovered_pages
                    SET discovery_status = ?,
                        decision_made_at = CURRENT_TIMESTAMP
                    WHERE target_page_id IN ({placeholders})
                """

            params.extend(page_ids)
            cursor = self.conn.execute(query, params)
            return cursor.rowcount

    def check_page_http_status(self, page_id: str, http_status: int) -> None:
        """Record HTTP status check for a discovered page.

        Args:
            page_id: Target page identifier
            http_status: HTTP status code returned
        """
        with self.transaction():
            self.conn.execute("""
                UPDATE discovered_pages
                SET http_status_code = ?,
                    last_check_at = CURRENT_TIMESTAMP,
                    check_attempt_count = check_attempt_count + 1
                WHERE target_page_id = ?
            """, (http_status, page_id))

    # Utility operations

    def get_all_page_ids(self, batch_id: str) -> set:
        """Get set of all page IDs converted in a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Set of page IDs
        """
        cursor = self.conn.execute("""
            SELECT DISTINCT page_id FROM pages WHERE batch_id = ?
        """, (batch_id,))
        return {row[0] for row in cursor.fetchall()}

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
