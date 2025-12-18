#!/usr/bin/env python3
"""Test discovery workflow status"""

from wikiaccess.database import ConversionDatabase

def main():
    print("\n" + "="*70)
    print("Discovery Workflow Status")
    print("="*70 + "\n")

    db = ConversionDatabase()

    # Get status counts
    discovered = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages WHERE discovery_status = "discovered"'
    ).fetchone()[0]

    approved = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages WHERE discovery_status = "approved"'
    ).fetchone()[0]

    skipped = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages WHERE discovery_status = "skipped"'
    ).fetchone()[0]

    converted = db.conn.execute(
        'SELECT COUNT(*) FROM discovered_pages WHERE discovery_status = "converted"'
    ).fetchone()[0]

    print("Page Status:")
    print(f"  Discovered (pending review): {discovered}")
    print(f"  Approved (ready for conversion): {approved}")
    print(f"  Skipped: {skipped}")
    print(f"  Converted: {converted}")

    total = discovered + approved + skipped + converted
    print(f"  TOTAL: {total}")

    if approved > 0:
        print(f"\n⚠️  {approved} pages ready for conversion!")
        print("   Run: python3 convert_approved.py")

    if discovered > 0:
        print(f"\n📋 {discovered} pages pending review")
        print("   Run: python3 review_discoveries.py")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
