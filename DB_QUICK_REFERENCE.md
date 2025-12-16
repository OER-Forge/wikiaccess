# Database Quick Reference

## Common Commands

### View All Batches
```bash
python db_query.py list-batches
```

### Check Batch Status
```bash
python db_query.py batch-info batch_20251216_143022
```

### Find Failed Pages
```bash
python db_query.py failed-pages batch_20251216_143022
```

### Track Page Improvements
```bash
python db_query.py page-history https://wiki.example.com namespace:page
```

### Analyze Image Problems
```bash
python db_query.py broken-images
```

### Export Results
```bash
python db_query.py export-csv batch_20251216_143022 results.csv
```

## Common Workflows

### 1. Resume Failed Conversions
```bash
# Check what failed
python db_query.py failed-pages batch_20251216_143022

# Edit URLS.txt to contain only failed pages
# Then re-run
python convert_from_file_list.py
```

### 2. Verify Accessibility Improvements
```bash
# Initial conversion
python convert_from_file_list.py

# Fix issues in markdown
nano output/markdown/page1.md

# Re-convert
python convert_from_markdown.py output/markdown/page1.md

# Check trend
python db_query.py accessibility-trends https://wiki.example.com page1
```

### 3. Generate Compliance Report
```bash
# Export last batch
python db_query.py list-batches  # Get latest batch_id
python db_query.py export-csv batch_YYYYMMDD_HHMMSS report.csv
```

## Python API Snippets

### Check if Page Needs Conversion
```python
from wikiaccess.database import ConversionDatabase

db = ConversionDatabase("output/conversion_history.db")
needs_conversion = not db.was_recently_converted(
    "https://wiki.example.com",
    "namespace:page",
    hours=24  # Within last 24 hours
)
db.close()
```

### Get Failed Pages Programmatically
```python
from wikiaccess.database import ConversionDatabase

db = ConversionDatabase("output/conversion_history.db")
failed = db.get_failed_pages("batch_20251216_143022")
print(f"Failed pages: {failed}")
db.close()
```

### Track Accessibility Trends
```python
from wikiaccess.database import ConversionDatabase

db = ConversionDatabase("output/conversion_history.db")
trends = db.get_accessibility_trends(
    "https://wiki.example.com",
    "namespace:page"
)

for record in trends:
    print(f"{record['converted_at']}: {record['html_wcag_aa_score']}%")

db.close()
```

## Disable Database (if needed)

```python
# In Python
from wikiaccess.unified import convert_multiple_pages

results = convert_multiple_pages(
    wiki_url="https://wiki.example.com",
    page_names=["page1"],
    use_database=False  # Disable database tracking
)
```

## Database Location

```
output/conversion_history.db
```

## Backup Database

```bash
cp output/conversion_history.db backup/conversion_history_$(date +%Y%m%d).db
```

## Reset Database

```bash
rm output/conversion_history.db
# Will be recreated on next conversion
```
