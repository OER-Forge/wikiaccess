#!/usr/bin/env python3
"""
Simple test script to verify database integration works correctly.
"""

import os
import tempfile
from wikiaccess.database import ConversionDatabase

def test_database():
    """Test basic database operations."""

    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = ConversionDatabase(db_path)

        print("✓ Database created successfully")

        # Test batch operations
        batch_id = "test_batch_001"
        wiki_url = "https://test.example.com"

        db.start_batch(batch_id, wiki_url)
        print("✓ Batch created successfully")

        # Test page conversion record
        page_data = {
            'wiki_url': wiki_url,
            'page_id': 'test:page',
            'batch_id': batch_id,
            'conversion_status': 'SUCCESS',
            'markdown_path': '/tmp/test.md',
            'html_path': '/tmp/test.html',
            'docx_path': '/tmp/test.docx',
            'html_wcag_aa_score': 85,
            'html_wcag_aaa_score': 75,
            'docx_wcag_aa_score': 90,
            'docx_wcag_aaa_score': 80,
            'image_count': 5,
            'image_success_count': 4,
            'image_failed_count': 1,
            'conversion_duration_seconds': 12.5,
            'error_message': None
        }

        page_id = db.add_page_conversion(page_data)
        print(f"✓ Page conversion recorded (ID: {page_id})")

        # Test image record
        image_data = {
            'page_id': 'test:page',
            'batch_id': batch_id,
            'type': 'wiki_image',
            'source_url': 'https://example.com/image.png',
            'local_filename': 'image.png',
            'status': 'success',
            'file_size': 12345,
            'dimensions': '800x600',
            'alt_text': 'Test image',
            'alt_text_quality': 'manual',
            'error_message': None
        }

        img_id = db.add_image(image_data)
        print(f"✓ Image record added (ID: {img_id})")

        # Test link record
        link_data = {
            'source_page_id': 'test:page',
            'target_page_id': 'test:other_page',
            'link_text': 'Link to other page',
            'link_type': 'internal',
            'resolution_status': 'found',
            'batch_id': batch_id
        }

        link_id = db.add_link(link_data)
        print(f"✓ Link record added (ID: {link_id})")

        # Test accessibility issue
        issue_data = {
            'page_id': 'test:page',
            'batch_id': batch_id,
            'format': 'HTML',
            'level': 'AA',
            'issue_code': 'missing-alt-text',
            'issue_message': 'Image missing alt text',
            'element_selector': 'img#test'
        }

        issue_id = db.add_accessibility_issue(issue_data)
        print(f"✓ Accessibility issue recorded (ID: {issue_id})")

        # Test batch completion
        stats = {
            'total_pages': 1,
            'successful_pages': 1,
            'failed_pages': 0,
            'total_images': 5,
            'failed_images': 1
        }

        db.complete_batch(batch_id, stats)
        print("✓ Batch completed successfully")

        # Test queries
        batch_info = db.get_batch_info(batch_id)
        assert batch_info is not None, "Batch info should exist"
        assert batch_info['total_pages'] == 1, "Total pages should be 1"
        print("✓ Batch info query works")

        history = db.get_page_history(wiki_url, 'test:page')
        assert len(history) == 1, "Should have 1 history record"
        print("✓ Page history query works")

        converted = db.get_converted_pages(batch_id)
        assert len(converted) == 1, "Should have 1 converted page"
        print("✓ Converted pages query works")

        all_pages = db.get_all_page_ids(batch_id)
        assert 'test:page' in all_pages, "Page should be in set"
        print("✓ All page IDs query works")

        # Test recent conversion check
        is_recent = db.was_recently_converted(wiki_url, 'test:page', hours=1)
        assert is_recent == True, "Page should be marked as recently converted"
        print("✓ Recent conversion check works")

        db.close()
        print("\n✅ All database tests passed!")

if __name__ == "__main__":
    test_database()
