#!/usr/bin/env python3
"""
Review discovered pages - Interactive CLI for managing page discoveries.

Usage:
    python review_discoveries.py              # Interactive review
    python review_discoveries.py --stats      # Show statistics
    python review_discoveries.py --export discovered_pages.txt  # Export to file
    python review_discoveries.py --bulk-approve  # Approve all discovered pages
"""

from wikiaccess.discovery_cli import main

if __name__ == '__main__':
    main()
