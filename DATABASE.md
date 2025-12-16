# WikiAccess Database Integration

## Overview

WikiAccess now includes SQLite database integration for persistent tracking of conversion history, accessibility metrics, image downloads, and links. This enables powerful features like:

- **Incremental updates**: Skip recently converted pages
- **Batch restart**: Resume failed conversions without re-processing successful pages
- **Accessibility trends**: Track WCAG scores over time
- **Image reliability**: Identify problematic image sources
- **Link tracking**: Monitor broken links and missing pages
- **Audit trails**: Complete history of all conversions

## Database Location

The database is automatically created at:
```
output/conversion_history.db
```

## Features

### 1. Automatic De-duplication

Pages converted within the last hour are automatically skipped to avoid redundant processing:

```python
from wikiaccess.unified import convert_multiple_pages

# Second run within an hour will skip already-converted pages
results = convert_multiple_pages(
    wiki_url="https://wiki.example.com",
    page_names=["page1", "page2", "page3"],
    use_database=True,
    skip_recent=True  # Default: True
)
```

### 2. Batch Tracking

Every conversion run is assigned a unique batch ID for grouping related conversions:

```
batch_20251216_143022  # Format: batch_YYYYMMDD_HHMMSS
```

### 3. Conversion History

Track every conversion attempt with:
- Conversion status (SUCCESS/FAILED/PARTIAL)
- WCAG accessibility scores (HTML & DOCX, AA & AAA levels)
- Image download statistics
- Processing duration
- Error messages

### 4. Image Tracking

Every image download is recorded with:
- Source URL
- Local filename
- Download status (success/failed/cached/skipped/error)
- Alt-text and quality assessment
- File size and dimensions

### 5. Link Tracking

Links between pages are recorded with:
- Source and target pages
- Link type (internal/external/anchor)
- Resolution status (found/missing/external)

### 6. Accessibility Tracking

WCAG issues are stored for:
- Trend analysis over time
- Issue type distribution
- Format comparison (HTML vs DOCX)

## Database Schema

### Tables

#### `conversion_batches`
- Tracks batch-level metadata
- Aggregated statistics (success/failure counts)

#### `pages`
- Individual page conversion records
- Accessibility scores and paths to outputs
- Image counts and processing time

#### `images`
- Image download attempts
- Alt-text quality tracking
- Failure analysis

#### `links`
- Link relationships between pages
- Broken link detection

#### `accessibility_issues`
- Individual WCAG violations
- Categorized by level (AA/AAA) and format (HTML/DOCX)

## Using the Database

### Python API

```python
from wikiaccess.database import ConversionDatabase

# Open database
db = ConversionDatabase("output/conversion_history.db")

# Get batch information
batch_info = db.get_batch_info("batch_20251216_143022")
print(f"Total pages: {batch_info['total_pages']}")
print(f"Successful: {batch_info['successful_pages']}")

# Get page history
history = db.get_page_history(
    wiki_url="https://wiki.example.com",
    page_id="namespace:page",
    limit=10
)

for record in history:
    print(f"Converted: {record['converted_at']}")
    print(f"HTML Score: {record['html_wcag_aa_score']}%")

# Get failed pages from a batch
failed = db.get_failed_pages("batch_20251216_143022")
print(f"Failed pages: {failed}")

# Check if page was recently converted
is_recent = db.was_recently_converted(
    wiki_url="https://wiki.example.com",
    page_id="namespace:page",
    hours=1
)

# Get image failure statistics
stats = db.get_image_failure_stats()
for stat in stats:
    print(f"{stat['source_url']}: {stat['failure_rate']}% failure rate")

# Get broken links
broken = db.get_broken_links("batch_20251216_143022")
for link in broken:
    print(f"{link['target_page_id']} referenced {link['reference_count']} times")

# Close connection
db.close()
```

### Command-Line Interface

The `db_query.py` utility provides convenient CLI access:

#### List all batches
```bash
python db_query.py list-batches
```

#### View batch details
```bash
python db_query.py batch-info batch_20251216_143022
```

#### View page conversion history
```bash
python db_query.py page-history https://wiki.example.com namespace:page
```

#### List failed pages in a batch
```bash
python db_query.py failed-pages batch_20251216_143022
```

#### Show broken/failed images
```bash
python db_query.py broken-images
```

#### Track accessibility trends for a page
```bash
python db_query.py accessibility-trends https://wiki.example.com namespace:page
```

#### Export batch data to CSV
```bash
python db_query.py export-csv batch_20251216_143022 output.csv
```

## Example Workflows

### Workflow 1: Incremental Conversion

Convert a large set of pages, then add more pages later without re-processing:

```bash
# Initial conversion (12 pages)
python convert_from_file_list.py

# Add new pages to URLS.txt

# Run again - only new pages are converted, existing ones are skipped
python convert_from_file_list.py
```

### Workflow 2: Retry Failed Conversions

```bash
# Run initial conversion
python convert_from_file_list.py

# Check which pages failed
python db_query.py failed-pages batch_20251216_143022

# Manually fix issues (network, credentials, etc.)

# Create new URLS.txt with only failed pages
python db_query.py failed-pages batch_20251216_143022 > failed_pages.txt

# Retry just the failed pages
# (Edit URLS.txt to contain only failed page URLs)
python convert_from_file_list.py
```

### Workflow 3: Track Accessibility Improvements

```bash
# Initial conversion
python convert_from_file_list.py

# Edit markdown files to fix accessibility issues
nano output/markdown/namespace_page.md

# Re-convert from markdown (faster, no scraping)
python convert_from_markdown.py output/markdown/namespace_page.md

# Check if scores improved
python db_query.py page-history https://wiki.example.com namespace:page

# Output shows trend:
# Date                 HTML Score   DOCX Score
# 2025-12-16 14:30:00  65%          70%
# 2025-12-16 15:45:00  82%          85%    ← Improved!
```

### Workflow 4: Analyze Image Download Problems

```bash
# After conversion, check image failures
python db_query.py broken-images

# Output shows:
# Source URL                              Failed  Total  Rate
# https://unreliable.com/images/...       45      50     90.0%
# https://example.com/media/...           2       100    2.0%

# Identify problematic servers and plan workarounds
```

### Workflow 5: Export for Compliance Reporting

```bash
# Export conversion results to CSV for stakeholders
python db_query.py export-csv batch_20251216_143022 conversion_report.csv

# CSV contains:
# - Page IDs
# - Conversion status
# - Accessibility scores (HTML & DOCX)
# - Image statistics
# - Error messages
```

## Disabling Database (Optional)

If you prefer to run without database tracking:

```python
results = convert_multiple_pages(
    wiki_url="https://wiki.example.com",
    page_names=["page1", "page2"],
    use_database=False  # Disable database
)
```

Or for single pages:

```python
result = convert_wiki_page(
    wiki_url="https://wiki.example.com",
    page_name="namespace:page",
    use_database=False
)
```

## Database Maintenance

### Backup
```bash
cp output/conversion_history.db output/conversion_history_backup.db
```

### Reset (delete all history)
```bash
rm output/conversion_history.db
# Database will be recreated on next conversion
```

### Optimize (shrink database size)
```bash
sqlite3 output/conversion_history.db "VACUUM;"
```

## Performance Notes

- Database operations add minimal overhead (~0.1-0.5s per page)
- SQLite is efficient for thousands of pages
- Indexes are automatically created for common queries
- Database size grows ~50KB per page conversion record

## Schema Diagram

```
conversion_batches
├── batch_id (PK)
├── wiki_url
├── started_at
├── completed_at
├── total_pages
├── successful_pages
└── failed_pages

pages
├── id (PK)
├── wiki_url
├── page_id
├── batch_id (FK)
├── conversion_status
├── markdown_path
├── html_path
├── docx_path
├── html_wcag_aa_score
├── html_wcag_aaa_score
├── docx_wcag_aa_score
├── docx_wcag_aaa_score
├── image_count
├── image_success_count
├── image_failed_count
├── converted_at
├── conversion_duration_seconds
└── error_message

images
├── id (PK)
├── page_id
├── batch_id
├── type
├── source_url
├── local_filename
├── status
├── file_size
├── dimensions
├── alt_text
├── alt_text_quality
└── error_message

links
├── id (PK)
├── source_page_id
├── target_page_id
├── link_text
├── link_type
├── resolution_status
└── batch_id

accessibility_issues
├── id (PK)
├── page_id
├── batch_id
├── format
├── level
├── issue_code
├── issue_message
└── element_selector
```

## Troubleshooting

### Database locked error
If you see "database is locked", ensure no other conversion process is running.

### Missing database
If database file doesn't exist, it will be created automatically on next conversion.

### Corrupted database
```bash
# Backup first
cp output/conversion_history.db output/conversion_history_corrupt.db

# Try to repair
sqlite3 output/conversion_history.db ".recover" | sqlite3 output/conversion_history_repaired.db

# If repair fails, delete and recreate
rm output/conversion_history.db
# Run conversion again to recreate
```

## Future Enhancements

Potential future features:
- Web dashboard for visualizing conversion history
- Automatic retry scheduling for failed conversions
- Email notifications for batch completion
- Link validation and automatic fixing
- Accessibility regression detection
- Multi-wiki tracking in single database
