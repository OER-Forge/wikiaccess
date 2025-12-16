#!/usr/bin/env python3
"""Test script for link rewriter"""

from wikiaccess.link_rewriter import LinkRewriter
from wikiaccess.database import ConversionDatabase

# Configuration
WIKI_URL = "https://msuperl.org/wikis/pcubed"
OUTPUT_DIR = "output"

# Initialize database
db = ConversionDatabase(f"{OUTPUT_DIR}/conversion_history.db")

# Create link rewriter
rewriter = LinkRewriter(WIKI_URL, OUTPUT_DIR, db)

# Run link rewriting
print("Testing link rewriter on existing HTML files...\n")
stats = rewriter.rewrite_all_links(batch_id="test_rewrite")

print(f"\n{'='*70}")
print("LINK REWRITING RESULTS")
print(f"{'='*70}")
print(f"Files processed: {stats['files_processed']}")
print(f"Links found: {stats['links_found']}")
print(f"Links rewritten: {stats['links_rewritten']}")
print(f"Broken links: {stats['links_broken']}")

# Generate broken links report
if stats['links_broken'] > 0:
    report_path = rewriter.generate_broken_links_report("test_rewrite")
    if report_path:
        print(f"\nBroken links report generated: {report_path}")

# Show database link counts
print(f"\n{'='*70}")
print("DATABASE LINK TRACKING")
print(f"{'='*70}")
cursor = db.conn.execute("SELECT COUNT(*) FROM links")
total_links = cursor.fetchone()[0]
print(f"Total links tracked: {total_links}")

cursor = db.conn.execute("SELECT link_type, COUNT(*) FROM links GROUP BY link_type")
print("\nBy type:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor = db.conn.execute("SELECT resolution_status, COUNT(*) FROM links GROUP BY resolution_status")
print("\nBy status:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

db.close()
