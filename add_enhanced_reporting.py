#!/usr/bin/env python3
"""Add enhanced reporting features to individual page reports"""

helper_methods = '''
    def _get_page_metadata(self, page_name: str) -> Dict:
        """Get page conversion metadata from database"""
        if not self.db:
            return {}

        try:
            cursor = self.db.conn.execute("""
                SELECT converted_at, conversion_duration_seconds,
                       image_count, image_success_count, image_failed_count
                FROM pages
                WHERE page_id = ?
                ORDER BY converted_at DESC LIMIT 1
            """, (page_name.replace('_', ':'),))
            row = cursor.fetchone()

            if row:
                # Get file sizes
                html_path = self.output_dir / 'html' / f'{page_name}.html'
                docx_path = self.output_dir / 'docx' / f'{page_name}.docx'
                md_path = self.output_dir / f'{page_name}.md'

                html_size = os.path.getsize(html_path) if html_path.exists() else 0
                docx_size = os.path.getsize(docx_path) if docx_path.exists() else 0
                md_size = os.path.getsize(md_path) if md_path.exists() else 0

                # Get word count from markdown
                word_count = 0
                if md_path.exists():
                    with open(md_path, 'r', encoding='utf-8') as f:
                        word_count = len(f.read().split())

                return {
                    'converted_at': row[0],
                    'duration': row[1],
                    'image_count': row[2],
                    'image_success': row[3],
                    'image_failed': row[4],
                    'html_size': html_size,
                    'docx_size': docx_size,
                    'md_size': md_size,
                    'word_count': word_count
                }
        except Exception as e:
            print(f"Error getting metadata: {e}")

        return {}

    def _get_page_links(self, page_name: str) -> Dict:
        """Get links for this page from database"""
        if not self.db:
            return {'outgoing': [], 'incoming': []}

        try:
            page_id = page_name.replace('_', ':')

            # Outgoing links
            cursor = self.db.conn.execute("""
                SELECT target_page_id, link_type, resolution_status, link_text
                FROM links
                WHERE source_page_id = ?
                ORDER BY link_type, target_page_id
            """, (page_id,))
            outgoing = [dict(row) for row in cursor.fetchall()]

            # Incoming links (backlinks)
            cursor = self.db.conn.execute("""
                SELECT source_page_id, link_text
                FROM links
                WHERE target_page_id = ? AND link_type = 'internal'
                ORDER BY source_page_id
            """, (page_id,))
            incoming = [dict(row) for row in cursor.fetchall()]

            return {'outgoing': outgoing, 'incoming': incoming}
        except Exception as e:
            print(f"Error getting links: {e}")

        return {'outgoing': [], 'incoming': []}

    def _get_page_images(self, page_name: str) -> List[Dict]:
        """Get images for this page from database"""
        if not self.db:
            return []

        try:
            cursor = self.db.conn.execute("""
                SELECT local_filename, source_url, status, alt_text, alt_text_quality, file_size
                FROM images
                WHERE page_id = ?
                ORDER BY id
            """, (page_name.replace('_', ':'),))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting images: {e}")

        return []

    def _get_version_history(self, page_name: str) -> List[Dict]:
        """Get conversion history for this page"""
        if not self.db:
            return []

        try:
            cursor = self.db.conn.execute("""
                SELECT converted_at, html_wcag_aa_score, html_wcag_aaa_score,
                       docx_wcag_aa_score, docx_wcag_aaa_score, conversion_status
                FROM pages
                WHERE page_id = ?
                ORDER BY converted_at DESC
                LIMIT 10
            """, (page_name.replace('_', ':'),))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting history: {e}")

        return []

    def _build_quick_actions(self, page_name: str, metadata: Dict) -> str:
        """Build quick actions panel"""
        html_path = f"../html/{page_name}.html"
        docx_path = f"../docx/{page_name}.docx"
        md_path = f"../{page_name}.md"

        return f"""
        <div class="quick-actions">
            <h3>Quick Actions</h3>
            <div class="actions-grid">
                <a href="{html_path}" class="action-btn" target="_blank">
                    <span class="action-icon">📄</span>
                    <span>View HTML</span>
                </a>
                <a href="{docx_path}" class="action-btn" download>
                    <span class="action-icon">📝</span>
                    <span>Download DOCX</span>
                </a>
                <a href="{md_path}" class="action-btn" target="_blank">
                    <span class="action-icon">📊</span>
                    <span>View Markdown</span>
                </a>
            </div>
        </div>
        """

    def _build_metadata_section(self, page_name: str, metadata: Dict) -> str:
        """Build metadata section"""
        if not metadata:
            return ""

        def format_size(bytes):
            for unit in ['B', 'KB', 'MB']:
                if bytes < 1024:
                    return f"{bytes:.1f} {unit}"
                bytes /= 1024
            return f"{bytes:.1f} GB"

        def format_duration(seconds):
            if seconds < 60:
                return f"{seconds:.1f}s"
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"

        return f"""
        <div class="metadata-section">
            <h3>Conversion Metadata</h3>
            <div class="metadata-grid">
                <div class="meta-item">
                    <span class="meta-label">Converted:</span>
                    <span class="meta-value">{metadata.get('converted_at', 'N/A')}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Duration:</span>
                    <span class="meta-value">{format_duration(metadata.get('duration', 0)) if metadata.get('duration') else 'N/A'}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Word Count:</span>
                    <span class="meta-value">{metadata.get('word_count', 0):,}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">HTML Size:</span>
                    <span class="meta-value">{format_size(metadata.get('html_size', 0))}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">DOCX Size:</span>
                    <span class="meta-value">{format_size(metadata.get('docx_size', 0))}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Images:</span>
                    <span class="meta-value">{metadata.get('image_success', 0)}/{metadata.get('image_count', 0)}</span>
                </div>
            </div>
        </div>
        """

    def _build_links_section(self, links: Dict) -> str:
        """Build links section"""
        if not links or (not links['outgoing'] and not links['incoming']):
            return ""

        outgoing_html = ""
        if links['outgoing']:
            outgoing_items = []
            for link in links['outgoing'][:20]:  # Show first 20
                icon = '✓' if link['resolution_status'] == 'found' else ('✗' if link['resolution_status'] == 'missing' else '↗')
                status_class = 'link-ok' if link['resolution_status'] == 'found' else ('link-broken' if link['resolution_status'] == 'missing' else 'link-external')
                outgoing_items.append(f"""
                    <div class="link-item {status_class}">
                        <span class="link-icon">{icon}</span>
                        <span class="link-target">{html_lib.escape(link['target_page_id'])}</span>
                        <span class="link-type">{link['link_type']}</span>
                    </div>
                """)
            outgoing_html = "".join(outgoing_items)

        incoming_html = ""
        if links['incoming']:
            incoming_items = []
            for link in links['incoming'][:10]:  # Show first 10
                incoming_items.append(f"""
                    <div class="backlink-item">
                        <span class="backlink-source">{html_lib.escape(link['source_page_id'])}</span>
                    </div>
                """)
            incoming_html = "".join(incoming_items)

        return f"""
        <div class="links-section">
            <h3>Links</h3>
            {f'''
            <div class="links-subsection">
                <h4>Outgoing Links ({len(links['outgoing'])})</h4>
                <div class="links-list">{outgoing_html}</div>
            </div>
            ''' if links['outgoing'] else ''}
            {f'''
            <div class="links-subsection">
                <h4>Referenced By ({len(links['incoming'])})</h4>
                <div class="backlinks-list">{incoming_html}</div>
            </div>
            ''' if links['incoming'] else ''}
        </div>
        """

    def _build_images_section(self, images: List[Dict]) -> str:
        """Build images section"""
        if not images:
            return ""

        images_html = []
        for img in images:
            quality_class = {
                'missing': 'quality-bad',
                'auto-generated': 'quality-warn',
                'manual': 'quality-good'
            }.get(img.get('alt_text_quality'), '')

            status_icon = '✓' if img['status'] in ['success', 'cached'] else '✗'

            images_html.append(f"""
                <div class="image-item">
                    <div class="image-info">
                        <div class="image-name">{html_lib.escape(img.get('local_filename', 'N/A'))}</div>
                        <div class="image-meta">
                            <span class="image-status">{status_icon} {img['status']}</span>
                            <span class="alt-quality {quality_class}">{img.get('alt_text_quality', 'unknown')}</span>
                        </div>
                    </div>
                </div>
            """)

        return f"""
        <div class="images-section">
            <h3>Images on This Page ({len(images)})</h3>
            <div class="images-grid">
                {"".join(images_html)}
            </div>
        </div>
        """

    def _build_history_section(self, history: List[Dict]) -> str:
        """Build version history section"""
        if not history or len(history) <= 1:
            return ""

        history_items = []
        for i, version in enumerate(history):
            is_current = i == 0
            badge = '<span class="current-badge">Current</span>' if is_current else ''

            history_items.append(f"""
                <div class="history-item {'history-current' if is_current else ''}">
                    <div class="history-date">{version['converted_at']}{badge}</div>
                    <div class="history-scores">
                        <span>HTML AA: {version.get('html_wcag_aa_score', 0)}%</span>
                        <span>DOCX AA: {version.get('docx_wcag_aa_score', 0)}%</span>
                    </div>
                </div>
            """)

        return f"""
        <div class="history-section">
            <h3>Version History ({len(history)} conversions)</h3>
            <div class="history-list">
                {"".join(history_items)}
            </div>
        </div>
        """
'''

# Read the file
with open('wikiaccess/reporting.py', 'r') as f:
    content = f.read()

# Find where to insert helper methods (before _build_combined_detail_html)
insert_point = content.find('    def _build_combined_detail_html(')
if insert_point == -1:
    print("Could not find insertion point")
    exit(1)

# Insert helper methods
content = content[:insert_point] + helper_methods + '\n' + content[insert_point:]

# Write back
with open('wikiaccess/reporting.py', 'w') as f:
    f.write(content)

print("✓ Added helper methods")
print("✓ Now adding enhanced sections to HTML template...")

# Now update the HTML template to include the new sections
with open('wikiaccess/reporting.py', 'r') as f:
    content = f.read()

# Find the sections div and add new sections after header
sections_marker = '        <div class="format-sections">'
if sections_marker in content:
    # Insert the enhanced sections before format-sections
    enhanced_sections = '''
        {quick_actions_html}
        {metadata_html}
        {links_html}
        {images_html}
        {history_html}

        '''
    content = content.replace(sections_marker, enhanced_sections + sections_marker)

    with open('wikiaccess/reporting.py', 'w') as f:
        f.write(content)

    print("✓ Added enhanced sections to template")
else:
    print("! Could not find format-sections marker")

print("\n✓ Enhanced reporting features added successfully!")
