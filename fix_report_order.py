#!/usr/bin/env python3
"""
Quick script to move the link rewriting before report generation
"""

with open('wikiaccess/unified.py', 'r') as f:
    content = f.read()

# Find the sections
accessibility_start = content.find("    # Generate combined accessibility report")
links_start = content.find("    # Rewrite internal links to point to local HTML files")
links_end = content.find("    # Generate broken links report if there are any", links_start) + len("        link_rewriter.generate_broken_links_report(batch_id, page_names_list)\n")

if accessibility_start == -1 or links_start == -1:
    print("Could not find sections")
    exit(1)

# Extract the link rewriting section
links_section = content[links_start:links_end]

# Remove it from its current position
content = content[:links_start] + content[links_end:]

# Insert it before accessibility report generation
new_accessibility_start = content.find("    # Generate combined accessibility report")
content = content[:new_accessibility_start] + links_section + "\n" + content[new_accessibility_start:]

# Write back
with open('wikiaccess/unified.py', 'w') as f:
    f.write(content)

print("✓ Moved link rewriting before report generation")
