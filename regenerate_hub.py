#!/usr/bin/env python3
"""Regenerate hub with link stats"""

from wikiaccess.hub_reporting import HubReportGenerator
from wikiaccess.database import ConversionDatabase
from pathlib import Path
import json

# Load previous conversion data from database
db = ConversionDatabase("output/conversion_history.db")

# Use the batch with broken links data
batch_id = "batch_20251216_103711"
print(f"Using batch: {batch_id}")

# Get page reports from database
cursor = db.conn.execute("""
    SELECT page_id, html_wcag_aa_score, html_wcag_aaa_score,
           docx_wcag_aa_score, docx_wcag_aaa_score
    FROM pages WHERE batch_id = ?
""", (batch_id,))

page_reports = {}
for row in cursor.fetchall():
    page_id = row[0].replace(':', '_')
    page_reports[page_id] = {
        'html': {
            'score_aa': row[1] or 0,
            'score_aaa': row[2] or 0,
            'issues_aa': [],
            'issues_aaa': []
        },
        'docx': {
            'score_aa': row[3] or 0,
            'score_aaa': row[4] or 0,
            'issues_aa': [],
            'issues_aaa': []
        },
        'html_stats': {},
        'docx_stats': {}
    }

# Get image details
cursor = db.conn.execute("""
    SELECT page_id, type, status, alt_text, alt_text_quality,
           local_filename, source_url, error_message
    FROM images WHERE batch_id = ?
""", (batch_id,))

image_details = []
for row in cursor.fetchall():
    image_details.append({
        'page_id': row[0],
        'type': row[1],
        'status': row[2],
        'alt_text': row[3],
        'alt_text_quality': row[4],
        'local_filename': row[5],
        'source_url': row[6],
        'error_message': row[7]
    })

# Get link stats
cursor = db.conn.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN link_type = 'internal' AND resolution_status = 'found' THEN 1 ELSE 0 END) as rewritten,
        SUM(CASE WHEN resolution_status = 'missing' THEN 1 ELSE 0 END) as broken
    FROM links WHERE batch_id = ?
""", (batch_id,))

row = cursor.fetchone()
link_stats = {
    'files_processed': len(page_reports),
    'links_found': row[0],
    'links_rewritten': row[1],
    'links_broken': row[2]
}

print(f"Page reports: {len(page_reports)}")
print(f"Image details: {len(image_details)}")
print(f"Link stats: {link_stats}")

# Generate hub
hub_gen = HubReportGenerator('output')
hub_path = hub_gen.generate_hub(page_reports, image_details, link_stats)

print(f"\nHub regenerated: {hub_path}")
db.close()
