#!/usr/bin/env python3
"""Test broken links analysis"""

from wikiaccess.database import ConversionDatabase

def main():
    print("\n" + "="*70)
    print("Broken Links Analysis")
    print("="*70 + "\n")

    db = ConversionDatabase()
    links = db.get_all_broken_links()

    print(f"Total unique missing pages: {len(links)}")
    total_refs = sum(l['reference_count'] for l in links)
    print(f"Total broken link references: {total_refs}\n")

    print("Top 10 most referenced missing pages:")
    for i, link in enumerate(sorted(links, key=lambda x: x['reference_count'], reverse=True)[:10], 1):
        print(f"  {i}. {link['target_page_id']}: {link['reference_count']} references")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
