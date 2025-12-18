#!/usr/bin/env python3
"""
WikiAccess - Markdown Converter

Converts DokuWiki content to Markdown as an intermediate format,
then uses Pandoc to generate HTML and DOCX.

This simplifies the codebase by:
1. Converting DokuWiki → Markdown (simple, single target)
2. Using Pandoc (battle-tested, standard) for Markdown → HTML/DOCX
3. Avoiding custom HTML/DOCX generation logic

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

import subprocess
import shutil
import urllib.request
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from .scraper import DokuWikiHTTPClient
from .parser import DokuWikiParser


class MarkdownConverter:
    """Convert DokuWiki content to Markdown, then to HTML/DOCX via Pandoc"""
    
    def __init__(self, client: DokuWikiHTTPClient, output_dir: Optional[str] = None,
                 include_accessibility_toolbar: bool = True):
        self.client = client
        self.parser = DokuWikiParser()
        self.output_dir = Path(output_dir) if output_dir else Path('output')
        self.markdown_dir = self.output_dir / 'markdown'
        self.images_dir = self.output_dir / 'images'
        self.html_dir = self.output_dir / 'html'
        self.docx_dir = self.output_dir / 'docx'
        self.reports_dir = self.output_dir / 'reports'
        self.current_page_id = None
        self.image_count = 0
        self.image_success = 0
        self.image_failed = 0

        # Configuration options
        self.include_accessibility_toolbar = include_accessibility_toolbar

        # Detailed image tracking for reporting
        self.image_details = []  # List of dicts with full image metadata

        # Create all directories
        for dir_path in [self.markdown_dir, self.images_dir, self.html_dir, self.docx_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Check if pandoc is installed
        if not shutil.which('pandoc'):
            raise RuntimeError("Pandoc is not installed. Install it with: brew install pandoc (macOS) or apt-get install pandoc (Linux)")
    
    
    def convert_url(self, url: str, document_title: Optional[str] = None) -> Tuple[str, str, Dict]:
        """
        Convert DokuWiki URL to Markdown, then to HTML and DOCX
        
        Creates flat folder structure:
            output/
            ├── markdown/
            │   ├── page1.md
            │   └── page2.md
            ├── images/
            │   ├── page1_image1.png
            │   ├── page2_image1.jpg
            │   └── youtube_[video_id].jpg
            ├── html/
            │   ├── page1.html
            │   └── page2.html
            ├── docx/
            │   ├── page1.docx
            │   └── page2.docx
            └── reports/
                ├── accessibility_report.html
                └── page1_accessibility.html
        
        Returns:
            Tuple of (html_path, docx_path, stats_dict)
        """
        print(f"\n🌐 Converting URL to Markdown: {url}")
        print("=" * 70)
        
        # Fetch page content
        result = self.client.get_page_from_url(url)
        if not result:
            print("✗ Failed to fetch page content")
            return None, None, {}
        
        page_id, content = result
        self.current_page_id = page_id
        
        # Generate title
        if document_title is None:
            document_title = page_id.replace('_', ' ').replace(':', ' - ').title()
        
        # Convert DokuWiki to Markdown
        markdown = self._convert_to_markdown(content, document_title)
        
        # Save markdown
        page_name = page_id.replace(':', '_')
        md_path = self.markdown_dir / f"{page_name}.md"
        md_path.write_text(markdown, encoding='utf-8')
        print(f"✓ Markdown generated: {md_path}")
        
        # Convert Markdown to HTML
        html_path = self.html_dir / f"{page_name}.html"
        self._pandoc_convert(str(md_path), str(html_path), 'html', document_title)

        # Convert Markdown to DOCX
        docx_path = self.docx_dir / f"{page_name}.docx"
        self._pandoc_convert(str(md_path), str(docx_path), 'docx', document_title)
        
        stats = {
            'images': self.image_count,
            'images_success': self.image_success,
            'images_failed': self.image_failed
        }
        
        print(f"✓ HTML: {html_path}")
        print(f"✓ DOCX: {docx_path}")
        print(f"  📊 Images: {self.image_success}/{self.image_count}")
        
        return str(html_path), str(docx_path), stats
    
    def _convert_to_markdown(self, dokuwiki_content: str, title: str) -> str:
        """Convert DokuWiki syntax to Markdown"""
        lines = dokuwiki_content.split('\n')
        md_lines = []
        
        # Add title
        md_lines.append(f"# {title}\n")
        
        self.image_count = 0
        self.image_success = 0
        self.image_failed = 0
        
        in_list = False
        
        for line in lines:
            parsed = self.parser.parse_line(line)
            
            if parsed['type'] == 'heading':
                if in_list:
                    md_lines.append('')
                    in_list = False
                level = parsed['level']
                text = self._process_inline(parsed['content'])
                md_lines.append(f"{'#' * (level + 1)} {text}\n")
            
            elif parsed['type'] == 'paragraph':
                if in_list:
                    md_lines.append('')
                    in_list = False
                text = self._process_inline(parsed['content'])
                if text.strip():
                    md_lines.append(f"{text}\n")
            
            elif parsed['type'] == 'list_item':
                if not in_list:
                    in_list = True
                text = self._process_inline(parsed['content'])
                md_lines.append(f"- {text}\n")
            
            elif parsed['type'] == 'image':
                if in_list:
                    md_lines.append('')
                    in_list = False
                md_lines.append(self._process_image(parsed))
            
            elif parsed['type'] == 'youtube':
                if in_list:
                    md_lines.append('')
                    in_list = False
                video_id = parsed['video_id']
                md_lines.append(f"![Video: {video_id}](https://www.youtube.com/watch?v={video_id})\n")
            
            elif parsed['type'] == 'equation_block':
                if in_list:
                    md_lines.append('')
                    in_list = False
                equation = parsed['content']
                md_lines.append(f"$$\n{equation}\n$$\n")
            
            elif parsed['type'] == 'empty':
                if in_list:
                    md_lines.append('')
                    in_list = False
        
        if in_list:
            md_lines.append('')
        
        return '\n'.join(md_lines)
    
    def _process_inline(self, text: str) -> str:
        """Process inline formatting (bold, italic, links, equations)"""
        elements = self.parser.parse_inline_formatting(text)
        md_parts = []
        
        for elem_type, elem_data in elements:
            if elem_type == 'text':
                md_parts.append(elem_data['content'])
            elif elem_type == 'bold':
                inner = self._process_inline(elem_data['content'])
                md_parts.append(f"**{inner}**")
            elif elem_type == 'italic':
                inner = self._process_inline(elem_data['content'])
                md_parts.append(f"*{inner}*")
            elif elem_type == 'underline':
                inner = self._process_inline(elem_data['content'])
                md_parts.append(f"__{inner}__")  # Markdown doesn't have underline, use emphasis
            elif elem_type == 'link':
                url = elem_data['url']
                if not url.startswith('http'):
                    url = self.client.resolve_internal_link(url, self.current_page_id)
                link_text = elem_data['text']
                md_parts.append(f"[{link_text}]({url})")
            elif elem_type == 'equation_inline':
                eq = elem_data['content']
                md_parts.append(f"${eq}$")
        
        return ''.join(md_parts)
    
    def _process_image(self, parsed: dict) -> str:
        """Download image and return Markdown reference with detailed tracking"""
        image_path = parsed['path']
        width = parsed.get('width')
        timestamp = datetime.now().isoformat()

        # Check for YouTube videos - download thumbnail and create link
        if 'youtube>' in image_path:
            video_id = image_path.replace('youtube>', '').split('?')[0].strip()
            thumb_filename = f"youtube_{video_id}.jpg"
            thumb_path = self.images_dir / thumb_filename
            source_url = f"https://www.youtube.com/watch?v={video_id}"

            image_record = {
                'page_id': self.current_page_id,
                'type': 'youtube_thumbnail',
                'source_url': source_url,
                'local_filename': thumb_filename,
                'local_path': str(thumb_path),
                'timestamp': timestamp,
                'alt_text': f"Video: {video_id}",
                'status': 'pending',
                'error_message': None,
                'file_size': None,
                'dimensions': None
            }

            # Download thumbnail if not already present
            if not thumb_path.exists():
                try:
                    thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    urllib.request.urlretrieve(thumb_url, str(thumb_path))
                    self.image_success += 1
                    image_record['status'] = 'success'
                    image_record['file_size'] = os.path.getsize(thumb_path) if thumb_path.exists() else None
                    print(f"✓ Downloaded YouTube thumbnail: {thumb_filename}")
                except Exception as e:
                    print(f"  ⚠ Failed to download YouTube thumbnail {video_id}: {e}")
                    # Fallback to lower resolution if maxresdefault fails
                    try:
                        thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        urllib.request.urlretrieve(thumb_url, str(thumb_path))
                        self.image_success += 1
                        image_record['status'] = 'success'
                        image_record['file_size'] = os.path.getsize(thumb_path) if thumb_path.exists() else None
                    except Exception as e2:
                        self.image_failed += 1
                        image_record['status'] = 'failed'
                        image_record['error_message'] = f"Primary: {str(e)}, Fallback: {str(e2)}"
                        self.image_details.append(image_record)
                        return f"[Video: {video_id}](https://www.youtube.com/watch?v={video_id})\n"
            else:
                self.image_success += 1
                image_record['status'] = 'cached'
                image_record['file_size'] = os.path.getsize(thumb_path) if thumb_path.exists() else None

            self.image_count += 1
            self.image_details.append(image_record)
            # Return Markdown with thumbnail that links to video
            return f"[![Video: {video_id}](images/{thumb_filename})](https://www.youtube.com/watch?v={video_id})\n"
        
        # Skip URL embeds
        if 'url>' in image_path or image_path.startswith('http'):
            self.image_details.append({
                'page_id': self.current_page_id,
                'type': 'external_url',
                'source_url': image_path,
                'local_filename': None,
                'local_path': None,
                'timestamp': timestamp,
                'alt_text': 'External content',
                'status': 'skipped',
                'error_message': 'External URL embed - not downloaded',
                'file_size': None,
                'dimensions': None
            })
            return f"[External content: {image_path}]\n"

        # Clean up image path
        clean_path = image_path.split('|')[0].split('?')[0].strip()

        # Extract alt text if provided
        alt_text = ''
        if '|' in image_path:
            parts = image_path.split('|')
            if len(parts) > 1:
                alt_text = parts[1].strip()

        try:
            # Generate filename
            filename = Path(clean_path).name
            if not filename:
                filename = f"image_{self.image_count}.png"

            save_path = self.images_dir / filename

            # Create image record
            image_record = {
                'page_id': self.current_page_id,
                'type': 'wiki_image',
                'source_url': clean_path,
                'local_filename': filename,
                'local_path': str(save_path),
                'timestamp': timestamp,
                'alt_text': alt_text or filename.replace('_', ' ').replace('-', ' ').rsplit('.', 1)[0],
                'status': 'pending',
                'error_message': None,
                'file_size': None,
                'dimensions': None
            }

            # Download using client
            success = self.client.download_media(clean_path, str(save_path))

            self.image_count += 1

            if success:
                self.image_success += 1
                image_record['status'] = 'success'

                # Get file metadata
                if save_path.exists():
                    image_record['file_size'] = os.path.getsize(save_path)
                    # Try to get image dimensions
                    try:
                        from PIL import Image
                        with Image.open(save_path) as img:
                            image_record['dimensions'] = f"{img.width}x{img.height}"
                    except:
                        image_record['dimensions'] = 'unknown'

                self.image_details.append(image_record)

                # Generate alt text if not provided
                if not alt_text:
                    alt_text = filename.replace('_', ' ').replace('-', ' ').rsplit('.', 1)[0]

                # Return Markdown image reference - Pandoc will resolve via resource-path
                return f"![{alt_text}](images/{filename})\n"
            else:
                self.image_failed += 1
                image_record['status'] = 'failed'
                image_record['error_message'] = 'Download failed - client returned False'
                self.image_details.append(image_record)
                return f"[Image: {clean_path}]\n"

        except Exception as e:
            self.image_count += 1
            self.image_failed += 1
            error_msg = str(e)
            print(f"  ⚠ Image download failed: {clean_path} - {error_msg}")

            self.image_details.append({
                'page_id': self.current_page_id,
                'type': 'wiki_image',
                'source_url': clean_path,
                'local_filename': filename if 'filename' in locals() else 'unknown',
                'local_path': None,
                'timestamp': timestamp,
                'alt_text': alt_text or 'unknown',
                'status': 'error',
                'error_message': error_msg,
                'file_size': None,
                'dimensions': None
            })
            return f"[Image: {clean_path}]\n"
    
    def _pandoc_convert(self, md_path: str, output_path: str, format_type: str, title: str = None):
        """
        Use Pandoc to convert Markdown to target format

        Args:
            md_path: Path to markdown file
            output_path: Path to save output
            format_type: 'html' or 'docx'
            title: Document title for metadata (optional)
        """
        try:
            # Use provided title or default to WikiAccess
            if title is None:
                title = "WikiAccess Document"

            if format_type == 'html':
                # HTML with embedded CSS for accessibility and image resource path
                cmd = [
                    'pandoc',
                    md_path,
                    '-o', output_path,
                    '--from', 'markdown',
                    '--to', 'html5',
                    '--standalone',
                    '--mathjax',
                    '--metadata', f'title={title}',
                    '--variable', 'lang=en',
                    '--resource-path', str(self.output_dir)
                ]
                subprocess.run(cmd, check=True, capture_output=True)

                # Enhance HTML with accessible CSS
                self._enhance_html_accessibility(output_path)

            elif format_type == 'docx':
                # DOCX with image resource path, language metadata, and TITLE
                cmd = [
                    'pandoc',
                    md_path,
                    '-o', output_path,
                    '--from', 'markdown',
                    '--to', 'docx',
                    '--metadata', f'title={title}',
                    '--metadata', 'lang=en',
                    '--resource-path', str(self.output_dir)
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            
            print(f"✓ Pandoc conversion to {format_type.upper()}: {output_path}")
        
        except subprocess.CalledProcessError as e:
            print(f"✗ Pandoc conversion failed: {e}")
            raise
        except FileNotFoundError:
            print(f"✗ Pandoc not found. Install with: brew install pandoc")
            raise
    
    def _enhance_html_accessibility(self, html_path: str):
        """Add accessibility CSS, MathJax, and fix image paths for generated HTML"""
        import re
        html_content = Path(html_path).read_text(encoding='utf-8')

        # Fix image paths - change "images/file.png" to "../images/file.png"
        # since HTML is in html/ folder and images are in images/ folder
        html_content = html_content.replace('src="images/', 'src="../images/')

        # Extract and set proper page title from content
        # Look for the first h1 element that's NOT in a title-block-header
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
        if title_match:
            page_title = title_match.group(1).strip()
            # Clean up title (remove newlines, extra whitespace)
            page_title = ' '.join(page_title.split())
            # Only use if it's not "WikiAccess" (the placeholder title)
            if page_title and page_title != "WikiAccess":
                html_content = re.sub(r'<title>[^<]*</title>', f'<title>{page_title}</title>', html_content)

        # Remove the blank title-block-header (the one with just "WikiAccess")
        # Also remove any aria-hidden from figcaptions (critical accessibility fix)
        html_content = re.sub(
            r'<header\s+id="title-block-header">\s*<h1\s+class="title">[^<]*</h1>\s*</header>\n*',
            '',
            html_content
        )

        # Fix aria-hidden on figcaptions (they MUST be accessible)
        html_content = re.sub(
            r'<figcaption\s+aria-hidden="true">',
            '<figcaption>',
            html_content
        )

        # Fix heading hierarchy: ensure proper sequence (H1, H2, H3, etc.)
        # This prevents screen reader confusion from heading level jumps
        heading_map = {}  # Track heading level transformations

        def fix_heading(match):
            heading_tag = match.group(1)  # e.g., 'h1', 'h6'
            level = int(heading_tag[1])  # Extract the digit (1-6)
            attrs = match.group(2)
            content = match.group(3)

            # Rules for heading hierarchy:
            # H1 can only follow body start
            # H6, H5 after H1 should be H2
            # H5 after H1 should be H2
            # Skip backwards in levels, bring forward

            # For now, convert H6 and H5 to H2 if they appear early
            # More sophisticated logic could track context
            if level >= 5 and '<h2' not in ''.join(list(heading_map.values())[:3]):
                level = 2

            heading_map[content[:20]] = f'h{level}'
            return f'<h{level}{attrs}>{content}</h{level}>'

        # Only apply if we detect heading hierarchy issues
        html_content = re.sub(
            r'<(h[1-6])([^>]*)>([^<]+)</h[1-6]>',
            fix_heading,
            html_content
        )

        # Add accessibility controls toolbar before content (if enabled)
        if self.include_accessibility_toolbar and '<body>' in html_content:
            accessibility_toolbar = '''    <!-- Accessibility Toolbar Toggle -->
    <button id="a11y-toggle-btn" class="a11y-toggle-btn" onclick="A11y.toggleToolbar()"
            aria-label="Show accessibility controls" title="Click to show accessibility options">ℹ</button>

    <!-- Accessibility Toolbar (Hidden by default) -->
    <div id="a11y-toolbar-content" class="accessibility-toolbar hidden" role="toolbar" aria-label="Accessibility controls">
        <!-- Screen reader announcement region -->
        <div id="a11y-status" class="sr-only" aria-live="polite" aria-atomic="true"></div>

        <!-- Theme Section -->
        <div class="a11y-section">
            <span class="a11y-section-label">Theme</span>
            <button id="theme-toggle" class="a11y-btn a11y-theme-btn" onclick="A11y.toggleTheme()"
                    aria-label="Light mode - click to switch to dark mode"
                    title="Toggle between light and dark mode (Keyboard: Alt+T)"
                    aria-pressed="false">☀️ Light</button>
        </div>

        <!-- Text Section -->
        <div class="a11y-section">
            <span class="a11y-section-label">Text</span>
            <div class="a11y-controls-row">
                <!-- Font Size Control (14-20px) -->
                <div class="a11y-control-group">
                    <label for="font-size-control" class="a11y-control-label">Size:</label>
                    <button class="a11y-btn-small" onclick="A11y.adjustFontSize(-1)"
                            aria-label="Decrease font size" title="Decrease text size">A−</button>
                    <span id="font-size-display" class="a11y-control-value" aria-live="polite">16px</span>
                    <button class="a11y-btn-small" onclick="A11y.adjustFontSize(1)"
                            aria-label="Increase font size" title="Increase text size">A+</button>
                </div>

                <!-- Line Height Control (1.4-2.0) -->
                <div class="a11y-control-group">
                    <label for="line-height-control" class="a11y-control-label">Spacing:</label>
                    <button class="a11y-btn-small" onclick="A11y.adjustLineHeight(-0.1)"
                            aria-label="Decrease line height" title="Decrease spacing between lines">−</button>
                    <span id="line-height-display" class="a11y-control-value" aria-live="polite">1.7</span>
                    <button class="a11y-btn-small" onclick="A11y.adjustLineHeight(0.1)"
                            aria-label="Increase line height" title="Increase spacing between lines">+</button>
                </div>

                <!-- Letter Spacing Control -->
                <div class="a11y-control-group">
                    <label for="letter-spacing-control" class="a11y-control-label">Letters:</label>
                    <button class="a11y-btn-small" onclick="A11y.adjustLetterSpacing(-1)"
                            aria-label="Decrease letter spacing" title="Decrease spacing between letters">−</button>
                    <span id="letter-spacing-display" class="a11y-control-value" aria-live="polite">0</span>
                    <button class="a11y-btn-small" onclick="A11y.adjustLetterSpacing(1)"
                            aria-label="Increase letter spacing" title="Increase spacing between letters">+</button>
                </div>
            </div>
        </div>

        <!-- Font & Display Section -->
        <div class="a11y-section">
            <span class="a11y-section-label">Display</span>
            <div class="a11y-controls-row">
                <!-- Font Family Dropdown -->
                <div class="a11y-control-group">
                    <label for="font-family-select" class="a11y-control-label">Font:</label>
                    <select id="font-family-select" class="a11y-select"
                            onchange="A11y.setFontFamily(this.value)"
                            aria-label="Select accessible font family">
                        <option value="default">Standard</option>
                        <option value="atkinson">Atkinson Hyperlegible (Low Vision)</option>
                        <option value="opendyslexic">OpenDyslexic (Dyslexia)</option>
                        <option value="lexend">Lexend (Reading Speed)</option>
                        <option value="luciole">Luciole (Visual Impairment)</option>
                    </select>
                </div>

                <!-- High Contrast Toggle -->
                <button id="contrast-toggle" class="a11y-btn" onclick="A11y.toggleHighContrast()"
                        aria-label="High contrast off - click to enable"
                        title="Toggle high contrast mode for better visibility">
                    🎨 Contrast
                </button>
            </div>
        </div>

        <!-- Reset Button -->
        <button id="reset-btn" class="a11y-btn-reset" onclick="A11y.resetPreferences()"
                aria-label="Reset all accessibility settings to defaults"
                title="Reset accessibility preferences (Keyboard: Alt+R)">↺ Reset</button>
    </div>\n'''
            html_content = html_content.replace('<body>', '<body>\n' + accessibility_toolbar)

        # Wrap main content with proper <main> element before closing </body>
        # Find the body content and wrap it properly
        if '<body>' in html_content and '</body>' in html_content:
            # Find the first h1 tag (which should be the content title)
            body_start = html_content.find('<body>') + 6
            body_end = html_content.rfind('</body>')

            # Extract body content
            body_content = html_content[body_start:body_end]

            # Find skip link and first h1
            skip_link_pattern = r'<a href="#main-content"[^>]*>.*?</a>\n*'
            body_content_no_skip = re.sub(skip_link_pattern, '', body_content)

            # Now wrap content after skip link in <main>
            h1_match = re.search(r'<h1', body_content_no_skip)
            if h1_match:
                insert_pos = h1_match.start()
                skip_content = body_content[:insert_pos]  # content before h1 (skip link)
                main_content = body_content_no_skip[insert_pos:]  # h1 onwards

                # Reconstruct with proper <main> wrapper
                new_body_content = skip_content + '<main id="main-content">\n' + main_content + '</main>\n'
                html_content = html_content[:body_start] + new_body_content + html_content[body_end:]

        # Insert MathJax configuration, accessibility enhancements, theme controller, and CSS before closing </head>
        mathjax_and_css = """
    <!-- MathJax configuration for accessibility -->
    <script>
      window.MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
          displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
        },
        options: {
          enableMenu: true,
          menuSettings: {
            enableAccessibility: true,
            assistiveMML: true
          }
        },
        svg: { fontCache: 'global' },
        startup: {
          pageReady: () => {
            return MathJax.typesetPromise();
          }
        }
      };
    </script>
    <!-- MathJax library (single load, not duplicated) -->
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <!-- Comprehensive Accessibility Controller JavaScript -->
    <script>
      // WikiAccess Accessibility Manager
      const A11y = {
        // Default settings
        defaults: {
          theme: 'light',
          fontSize: 16,
          lineHeight: 1.7,
          letterSpacing: 0,
          fontFamily: 'default',
          highContrast: false
        },

        // Initialize on page load
        init: function() {
          // Load saved preferences or detect system preference
          const savedTheme = localStorage.getItem('wikiAccessTheme');
          if (savedTheme) {
            this.theme = savedTheme;
          } else {
            // Detect system dark mode preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.theme = prefersDark ? 'dark' : 'light';
          }
          this.fontSize = parseInt(localStorage.getItem('wikiAccessFontSize')) || this.defaults.fontSize;
          this.lineHeight = parseFloat(localStorage.getItem('wikiAccessLineHeight')) || this.defaults.lineHeight;
          this.letterSpacing = parseInt(localStorage.getItem('wikiAccessLetterSpacing')) || this.defaults.letterSpacing;
          this.fontFamily = localStorage.getItem('wikiAccessFontFamily') || this.defaults.fontFamily;
          this.highContrast = localStorage.getItem('wikiAccessHighContrast') === 'true';

          // Apply saved preferences
          this.applyTheme(this.theme);
          this.applyFontSize(this.fontSize);
          this.applyLineHeight(this.lineHeight);
          this.applyLetterSpacing(this.letterSpacing);
          this.applyFontFamily(this.fontFamily);
          this.applyHighContrast(this.highContrast);

          // Update all control displays
          this.updateAllControls();
        },

        // Theme management (Light/Dark mode)
        applyTheme: function(theme) {
          document.documentElement.setAttribute('data-theme', theme);
          this.theme = theme;
          localStorage.setItem('wikiAccessTheme', theme);
        },

        toggleTheme: function() {
          const newTheme = this.theme === 'light' ? 'dark' : 'light';
          this.applyTheme(newTheme);
          this.announceToScreenReader('Theme changed to ' + newTheme + ' mode');
          this.updateThemeButton();
        },

        // 1. Font Size Control (14px - 20px) - Increment/Decrement
        adjustFontSize: function(delta) {
          let newSize = this.fontSize + (delta * 2);
          newSize = Math.max(14, Math.min(20, newSize));
          this.fontSize = newSize;
          document.documentElement.style.fontSize = newSize + 'px';
          localStorage.setItem('wikiAccessFontSize', newSize);
          this.announceToScreenReader('Font size set to ' + newSize + ' pixels');
          this.updateControlDisplay('font-size-display', newSize + 'px');
        },

        applyFontSize: function(size) {
          document.documentElement.style.fontSize = size + 'px';
        },

        // 2. Line Height Control (1.4 - 2.0) - Increment/Decrement
        adjustLineHeight: function(delta) {
          let newHeight = Math.round((this.lineHeight + delta) * 10) / 10;
          newHeight = Math.max(1.4, Math.min(2.0, newHeight));
          this.lineHeight = newHeight;
          document.documentElement.style.setProperty('--line-height', newHeight);
          localStorage.setItem('wikiAccessLineHeight', newHeight);
          this.announceToScreenReader('Line height set to ' + newHeight);
          this.updateControlDisplay('line-height-display', newHeight.toFixed(1));
        },

        applyLineHeight: function(height) {
          document.documentElement.style.setProperty('--line-height', height);
        },

        // 3. Font Family Selection (Multiple accessible fonts)
        setFontFamily: function(family) {
          this.fontFamily = family;
          document.documentElement.setAttribute('data-font-family', family);
          localStorage.setItem('wikiAccessFontFamily', family);

          const fontNames = {
            'default': 'Standard',
            'atkinson': 'Atkinson Hyperlegible',
            'opendyslexic': 'OpenDyslexic',
            'lexend': 'Lexend',
            'luciole': 'Luciole'
          };

          this.announceToScreenReader('Font changed to ' + fontNames[family]);
          this.updateFontFamilySelect();
        },

        applyFontFamily: function(family) {
          document.documentElement.setAttribute('data-font-family', family);
        },

        // 4. High Contrast Toggle
        toggleHighContrast: function() {
          this.highContrast = !this.highContrast;
          if (this.highContrast) {
            document.documentElement.setAttribute('data-high-contrast', 'true');
          } else {
            document.documentElement.removeAttribute('data-high-contrast');
          }
          localStorage.setItem('wikiAccessHighContrast', this.highContrast);
          this.announceToScreenReader('High contrast ' + (this.highContrast ? 'enabled' : 'disabled'));
          this.updateContrastButton();
        },

        applyHighContrast: function(enabled) {
          if (enabled) {
            document.documentElement.setAttribute('data-high-contrast', 'true');
          } else {
            document.documentElement.removeAttribute('data-high-contrast');
          }
        },

        // 5. Letter Spacing Control (-1 to 10) - Increment/Decrement
        adjustLetterSpacing: function(delta) {
          let newSpacing = this.letterSpacing + delta;
          newSpacing = Math.max(-1, Math.min(10, newSpacing));
          this.letterSpacing = newSpacing;
          document.documentElement.style.setProperty('--letter-spacing', (newSpacing * 0.01) + 'em');
          localStorage.setItem('wikiAccessLetterSpacing', newSpacing);
          this.announceToScreenReader('Letter spacing adjusted');
          this.updateControlDisplay('letter-spacing-display', newSpacing);
        },

        applyLetterSpacing: function(spacing) {
          document.documentElement.style.setProperty('--letter-spacing', (spacing * 0.01) + 'em');
        },

        // Screen reader announcements
        announceToScreenReader: function(message) {
          const status = document.getElementById('a11y-status');
          if (status) {
            status.textContent = message;
          }
        },

        // Update individual control displays
        updateControlDisplay: function(elementId, value) {
          const elem = document.getElementById(elementId);
          if (elem) {
            elem.textContent = value;
          }
        },

        // Update font family dropdown selection
        updateFontFamilySelect: function() {
          const select = document.getElementById('font-family-select');
          if (select) {
            select.value = this.fontFamily;
          }
        },

        // Update high contrast button
        updateContrastButton: function() {
          const btn = document.getElementById('contrast-toggle');
          if (btn) {
            if (this.highContrast) {
              btn.textContent = '🎨 Contrast (ON)';
              btn.setAttribute('aria-label', 'High contrast on - click to disable');
              btn.classList.add('active');
            } else {
              btn.textContent = '🎨 Contrast';
              btn.setAttribute('aria-label', 'High contrast off - click to enable');
              btn.classList.remove('active');
            }
          }
        },

        // Update theme button
        updateThemeButton: function() {
          const btn = document.getElementById('theme-toggle');
          if (btn) {
            if (this.theme === 'dark') {
              btn.textContent = '🌙 Dark';
              btn.setAttribute('aria-label', 'Dark mode - click to switch to light mode');
              btn.setAttribute('aria-pressed', 'true');
            } else {
              btn.textContent = '☀️ Light';
              btn.setAttribute('aria-label', 'Light mode - click to switch to dark mode');
              btn.setAttribute('aria-pressed', 'false');
            }
          }
        },

        // Update all control displays
        updateAllControls: function() {
          this.updateControlDisplay('font-size-display', this.fontSize + 'px');
          this.updateControlDisplay('line-height-display', this.lineHeight.toFixed(1));
          this.updateControlDisplay('letter-spacing-display', this.letterSpacing);
          this.updateThemeButton();
          this.updateFontFamilySelect();
          this.updateContrastButton();
        },

        // Reset to defaults
        resetPreferences: function() {
          if (confirm('Reset all accessibility settings to default?')) {
            this.applyTheme(this.defaults.theme);
            this.applyFontSize(this.defaults.fontSize);
            this.applyLineHeight(this.defaults.lineHeight);
            this.applyLetterSpacing(this.defaults.letterSpacing);
            this.applyFontFamily(this.defaults.fontFamily);
            this.applyHighContrast(this.defaults.highContrast);

            // Update variables
            this.theme = this.defaults.theme;
            this.fontSize = this.defaults.fontSize;
            this.lineHeight = this.defaults.lineHeight;
            this.letterSpacing = this.defaults.letterSpacing;
            this.fontFamily = this.defaults.fontFamily;
            this.highContrast = this.defaults.highContrast;

            // Clear storage and update displays
            localStorage.clear();
            this.announceToScreenReader('Accessibility preferences reset to default');
            this.updateAllControls();
          }
        },

        // Toggle toolbar visibility
        toggleToolbar: function() {
          const toolbar = document.getElementById('a11y-toolbar-content');
          const toggleBtn = document.getElementById('a11y-toggle-btn');
          if (toolbar) {
            toolbar.classList.toggle('hidden');
            const isHidden = toolbar.classList.contains('hidden');
            toggleBtn.setAttribute('aria-label', isHidden ? 'Show accessibility controls' : 'Hide accessibility controls');
            this.announceToScreenReader(isHidden ? 'Accessibility toolbar hidden' : 'Accessibility toolbar shown');
          }
        }
      };

      // Initialize on page load
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => A11y.init());
      } else {
        A11y.init();
      }

      // Keyboard shortcuts for accessibility
      document.addEventListener('keydown', (e) => {
        // Alt + T: Toggle theme
        if (e.altKey && e.key === 't') {
          A11y.toggleTheme();
          e.preventDefault();
        }
        // Alt + R: Reset preferences
        if (e.altKey && e.key === 'r') {
          if (confirm('Reset accessibility settings to default?')) {
            A11y.resetPreferences();
          }
          e.preventDefault();
        }
      });
    </script>
    <style>
        /* Import accessible fonts from Google Fonts and other sources */
        @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=OpenDyslexic:wght@400;700&display=swap');

        /* Luciole font - hosted via CDN */
        @font-face {
            font-family: 'Luciole';
            src: url('https://www.luciole-vision.com/files/Luciole-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }

        :root {
            /* Light theme colors (default) - WCAG AAA compliant */
            --bg-primary: #ffffff;
            --bg-secondary: #f5f7fa;
            --text-primary: #1a1a1a;
            --text-secondary: #4a4a4a;
            --accent-primary: #0047b3;  /* Darker blue for 7:1 contrast ratio (AAA) */
            --accent-secondary: #003580;  /* Even darker for hover */
            --accent-btn-bg: #0047b3;  /* Button background for AAA compliance */
            --reset-btn-bg: #7a3e00;  /* Dark orange/brown for 7:1+ contrast (AAA) */
            --reset-btn-hover: #5c2e00;  /* Darker for hover */
            --border-color: #d0d7de;
            --code-bg: #f6f8fa;
            --link-visited: #4a1a7a;  /* Darker purple for AAA */
            --highlight-bg: #fffacd;

            /* Spacing and typography variables */
            --line-height: 1.7;
            --letter-spacing: 0em;
        }

        html[data-theme="dark"] {
            /* Dark theme colors - WCAG AAA compliant */
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --text-primary: #f0f6fc;
            --text-secondary: #c9d1d9;
            --accent-primary: #4a9eff;  /* Brighter blue for dark mode AAA */
            --accent-secondary: #6eb5ff;  /* Lighter for hover */
            --accent-btn-bg: #0066cc;  /* Button background for dark mode */
            --reset-btn-bg: #d97706;  /* Orange for dark mode */
            --reset-btn-hover: #f59e0b;  /* Brighter for hover */
            --border-color: #30363d;
            --code-bg: #161b22;
            --link-visited: #d4a5ff;  /* Brighter purple for dark mode */
            --highlight-bg: #463c0f;
        }

        /* High contrast mode - extreme accessibility */
        html[data-high-contrast="true"] {
            --bg-primary: #ffffff;
            --bg-secondary: #f0f0f0;
            --text-primary: #000000;
            --text-secondary: #000000;
            --accent-primary: #0000ff;
            --accent-secondary: #0000cc;
            --border-color: #000000;
            --code-bg: #f0f0f0;
            --link-visited: #660066;
            --highlight-bg: #ffff00;
        }

        html[data-theme="dark"][data-high-contrast="true"] {
            --bg-primary: #000000;
            --bg-secondary: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #ffffff;
            --accent-primary: #ffff00;
            --accent-secondary: #cccc00;
            --border-color: #ffffff;
            --code-bg: #1a1a1a;
            --link-visited: #ffccff;
            --highlight-bg: #ffff00;
        }

        /* High contrast mode - ensure borders are visible */
        html[data-high-contrast="true"] * {
            border-width: 2px !important;
        }

        html[data-high-contrast="true"] a {
            text-decoration-thickness: 3px !important;
        }

        * {
            box-sizing: border-box;
        }

        html {
            /* 16px = 1rem base for better scaling */
            font-size: 16px;
            scroll-behavior: smooth;
            color-scheme: light dark;
            background: var(--bg-primary);
            transition: background-color 0.3s ease;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Segoe UI Emoji", sans-serif;
            font-size: 1.125rem;
            line-height: var(--line-height);
            letter-spacing: var(--letter-spacing);
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem;
            color: var(--text-primary);
            background: var(--bg-primary);
            overflow-x: hidden;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        /* Hidden state for toolbar */
        .accessibility-toolbar.hidden {
            display: none !important;
        }

        /* Toggle button - floating at top right */
        .a11y-toggle-btn {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 9999;
            width: 44px;
            height: 44px;
            padding: 0;
            border: 2px solid #333;
            background: #f0f0f0;
            color: #333;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }

        .a11y-toggle-btn:hover {
            background: #e0e0e0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }

        .a11y-toggle-btn:focus {
            outline: 3px solid #333;
            outline-offset: 2px;
        }

        /* Dark mode button */
        [data-theme="dark"] .a11y-toggle-btn {
            border-color: #e0e0e0;
            background: #333;
            color: #e0e0e0;
        }

        [data-theme="dark"] .a11y-toggle-btn:hover {
            background: #444;
        }

        [data-theme="dark"] .a11y-toggle-btn:focus {
            outline-color: #e0e0e0;
        }

        /* Accessibility Toolbar - Modern Structure */
        .accessibility-toolbar {
            display: flex;
            gap: 1.5rem;
            align-items: center;
            padding: 1rem 1.5rem;
            background: var(--bg-secondary);
            border-bottom: 3px solid var(--border-color);
            margin: -2rem -2rem 2rem -2rem;
            flex-wrap: wrap;
            role: toolbar;
            justify-content: flex-start;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        /* Accessibility Section */
        .a11y-section {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            padding: 0.5rem;
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            border-radius: 6px;
            flex-shrink: 0;
        }

        .a11y-section-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
            text-align: center;
        }

        .a11y-controls-row {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
        }

        /* Control Groups */
        .a11y-control-group {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            background: var(--bg-secondary);
            padding: 0.4rem 0.6rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            flex-shrink: 0;
        }

        .a11y-control-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-secondary);
            white-space: nowrap;
            margin: 0;
            padding: 0;
        }

        .a11y-control-value {
            min-width: 3rem;
            text-align: center;
            font-weight: 600;
            color: var(--accent-primary);
            font-size: 0.95rem;
            padding: 0 0.25rem;
        }

        /* Select dropdown for font family */
        .a11y-select {
            padding: 0.4rem 0.6rem;
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 2px solid var(--accent-btn-bg);
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s ease;
            min-height: 36px;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%230047b3' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 0.5rem center;
            padding-right: 2rem;
        }

        .a11y-select:hover {
            border-color: var(--accent-secondary);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .a11y-select:focus {
            outline: 3px solid var(--accent-primary);
            outline-offset: 2px;
            border-color: var(--accent-primary);
        }

        /* Dark mode adjustments for select */
        html[data-theme="dark"] .a11y-select {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%234a9eff' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
        }

        /* Small buttons for increment/decrement - WCAG AAA compliant */
        .a11y-btn-small {
            padding: 0.4rem 0.6rem;
            background: var(--accent-btn-bg);
            color: white;
            border: 1px solid var(--accent-secondary);
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 700;
            transition: all 0.15s ease;
            min-width: 32px;
            min-height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
        }

        .a11y-btn-small:hover {
            background: var(--accent-secondary);
            transform: scale(1.08);
        }

        .a11y-btn-small:focus {
            outline: 3px solid var(--accent-primary);
            outline-offset: 2px;
        }

        .a11y-btn-small:active {
            transform: scale(0.95);
        }

        /* Regular toggle buttons - WCAG AAA compliant */
        .a11y-btn {
            padding: 0.5rem 0.85rem;
            background: var(--accent-btn-bg);
            color: white;
            border: 2px solid var(--accent-secondary);
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.2s ease;
            min-height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .a11y-btn:hover {
            background: var(--accent-secondary);
            transform: scale(1.05);
        }

        .a11y-btn:focus {
            outline: 3px solid var(--accent-primary);
            outline-offset: 2px;
        }

        .a11y-btn:active {
            transform: scale(0.98);
        }

        .a11y-btn.active {
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
            background: var(--accent-secondary);
        }

        /* Theme button - special styling */
        .a11y-theme-btn {
            min-width: 100px;
            font-size: 1rem;
        }

        /* Reset button - WCAG AAA compliant */
        .a11y-btn-reset {
            padding: 0.5rem 0.85rem;
            background: var(--reset-btn-bg);
            color: white;
            border: 2px solid var(--reset-btn-hover);
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s ease;
            min-height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            margin-left: auto;
            flex-shrink: 0;
        }

        .a11y-btn-reset:hover {
            background: var(--reset-btn-hover);
            transform: scale(1.05);
        }

        .a11y-btn-reset:focus {
            outline: 3px solid var(--reset-btn-bg);
            outline-offset: 2px;
        }

        .a11y-btn-reset:active {
            transform: scale(0.98);
        }

        /* Screen reader only text */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }

        main {
            padding: 1rem 0;
        }

        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5em;
            margin-bottom: 0.75em;
            font-weight: 600;
            line-height: 1.3;
            letter-spacing: -0.01em;
            color: var(--text-primary);
        }

        h1 {
            font-size: 2.5rem;
        }

        h2 {
            font-size: 1.875rem;
        }

        h3 {
            font-size: 1.5rem;
        }

        h4, h5, h6 {
            font-size: 1.25rem;
        }

        p {
            margin: 1em 0;
        }

        a {
            color: var(--accent-primary);
            text-decoration: underline;
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
            transition: color 0.2s ease, background-color 0.2s ease;
        }

        a:visited {
            color: var(--link-visited);
        }

        a:hover {
            color: var(--accent-secondary);
            background-color: rgba(0, 82, 204, 0.1);
        }

        a:focus {
            outline: 3px solid var(--accent-primary);
            outline-offset: 2px;
            border-radius: 2px;
        }

        a:active {
            color: var(--accent-secondary);
        }

        /* Accessible font families via data-font-family attribute */
        html[data-font-family="default"] body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Segoe UI Emoji", sans-serif;
        }

        html[data-font-family="atkinson"] body {
            font-family: "Atkinson Hyperlegible", -apple-system, BlinkMacSystemFont, sans-serif;
        }

        html[data-font-family="opendyslexic"] body {
            font-family: "OpenDyslexic", "Comic Sans MS", cursive, sans-serif;
        }

        html[data-font-family="lexend"] body {
            font-family: "Lexend", -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: 0.02em; /* Lexend benefits from slight letter spacing */
        }

        html[data-font-family="luciole"] body {
            font-family: "Luciole", -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: 0.03em; /* Luciole designed with wider spacing */
        }

        img, svg {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em 0;
        }

        img {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }

        figure {
            margin: 2em 0;
            padding: 1em;
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-primary);
            border-radius: 4px;
        }

        figcaption {
            font-style: italic;
            color: var(--text-secondary);
            margin-top: 1em;
            font-size: 0.95rem;
        }

        code {
            background: var(--code-bg);
            color: var(--text-primary);
            padding: 0.25em 0.5em;
            border-radius: 3px;
            font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Menlo, Consolas, "Courier New", monospace;
            font-size: 0.9em;
            border: 1px solid var(--border-color);
        }

        pre {
            background: var(--code-bg);
            color: var(--text-primary);
            padding: 1.5em;
            border-left: 4px solid var(--accent-primary);
            border-radius: 4px;
            overflow-x: auto;
            line-height: 1.4;
            border: 1px solid var(--border-color);
        }

        pre code {
            background: transparent;
            padding: 0;
            font-size: 0.9em;
            border: none;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2em 0;
            font-variant-numeric: lining-nums tabular-nums;
            overflow-x: auto;
            display: block;
        }

        thead {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        th {
            text-align: left;
            padding: 0.75em;
            border: 1px solid var(--border-color);
            font-weight: 600;
            color: var(--text-primary);
        }

        td {
            padding: 0.75em;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }

        tbody tr:nth-child(even) {
            background: var(--bg-secondary);
        }

        blockquote {
            margin: 1.5em 0;
            padding-left: 1.5em;
            border-left: 4px solid var(--accent-primary);
            color: var(--text-secondary);
            font-style: italic;
            background: var(--bg-secondary);
            padding: 1em 1em 1em 1.5em;
            border-radius: 4px;
        }

        ol, ul {
            margin: 1.5em 0;
            padding-left: 2em;
        }

        li {
            margin-bottom: 0.5em;
        }

        hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 2em 0;
        }

        /* Skip link - visually hidden but keyboard accessible */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: var(--accent-primary);
            color: var(--bg-primary);
            padding: 8px 12px;
            text-decoration: none;
            z-index: 1000;
            border-radius: 0 0 4px 0;
            font-weight: 600;
            transition: top 0.2s ease;
        }

        .skip-link:focus {
            top: 0;
            outline: 3px solid var(--accent-secondary);
            outline-offset: -3px;
        }

        /* Reduced motion support for users who prefer it */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation: none !important;
                transition: none !important;
                scroll-behavior: auto !important;
            }
        }

        /* Smooth transitions between themes */
        html[data-theme="auto"] {
            color-scheme: light dark;
        }

        html[data-theme="light"] {
            color-scheme: light;
        }

        html[data-theme="dark"] {
            color-scheme: dark;
        }

        /* Ensure reduced motion respects theme transitions */
        @media (prefers-reduced-motion: reduce) {
            body {
                transition: none;
            }
        }

        /* High contrast mode */
        @media (prefers-contrast: more) {
            a {
                text-decoration-thickness: 3px;
            }

            a:focus {
                outline-width: 4px;
            }

            button, input {
                border-width: 2px;
            }

            h1, h2, h3 {
                text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5);
            }
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            body {
                font-size: 1rem;
                padding: 1rem;
            }

            h1 {
                font-size: 1.875rem;
            }

            h2 {
                font-size: 1.5rem;
            }

            h3 {
                font-size: 1.25rem;
            }

            h4, h5, h6 {
                font-size: 1.125rem;
            }

            table {
                font-size: 0.95rem;
            }

            th, td {
                padding: 0.5em;
            }

            figure {
                padding: 0.75em;
            }

            ol, ul {
                padding-left: 1.5em;
            }
        }

        @media (max-width: 480px) {
            body {
                font-size: 0.95rem;
                padding: 0.75rem;
            }

            h1 {
                font-size: 1.5rem;
                margin-top: 1em;
            }

            h2 {
                font-size: 1.25rem;
            }

            h3 {
                font-size: 1.125rem;
            }

            main {
                padding: 0;
            }

            table {
                display: block;
                overflow-x: auto;
                font-size: 0.9rem;
            }

            pre {
                padding: 1em;
                font-size: 0.85rem;
            }

            code {
                font-size: 0.85em;
            }

            img {
                margin: 1em 0;
            }

            blockquote {
                padding-left: 1em;
            }

            ol, ul {
                padding-left: 1.25em;
            }
        }

        /* Table of Contents accessibility improvements */
        #TOC {
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1.5em;
            margin: 2em 0;
        }

        #TOC h2 {
            margin-top: 0;
            font-size: 1.25rem;
        }

        #TOC li {
            list-style: none;
        }

        #TOC ul {
            padding-left: 1.5em;
        }

        #TOC > ul {
            padding-left: 0;
        }

        /* Keep TOC links underlined for accessibility (don't hide underlines on non-hover) */
        #TOC a {
            text-decoration: underline;
            text-decoration-color: #0052cc;
        }

        #TOC a:hover {
            color: #003fa3;
            background-color: rgba(0, 82, 204, 0.1);
        }

        #TOC a:focus {
            outline: 3px solid #0052cc;
            outline-offset: 2px;
        }

        /* Landmark region styling */
        header {
            border-bottom: 2px solid #ddd;
            margin-bottom: 2em;
            padding-bottom: 1em;
        }

        nav {
            margin: 2em 0;
        }

        footer {
            border-top: 2px solid #ddd;
            margin-top: 3em;
            padding-top: 1em;
            font-size: 0.9rem;
            color: #666;
        }

        /* Math content accessibility */
        .math {
            font-size: 1em;
            overflow-x: auto;
        }

        .math.display {
            display: block;
            margin: 1em 0;
            text-align: center;
        }

        .math.inline {
            display: inline;
        }

        /* Accessible skip link for mobile */
        @media (max-width: 768px) {
            .skip-link {
                padding: 10px 15px;
                font-size: 0.9rem;
            }
        }

        /* Print styles */
        @media print {
            body {
                max-width: 100%;
                margin: 0;
                padding: 0;
                background: white;
                color: black;
            }

            a {
                color: black;
                text-decoration: underline;
            }

            a:after {
                content: " (" attr(href) ")";
                font-size: 0.8em;
            }

            h1, h2, h3 {
                page-break-after: avoid;
            }

            p, li {
                orphans: 3;
                widows: 3;
            }

            header, nav, footer {
                page-break-inside: avoid;
            }

            #TOC {
                page-break-after: avoid;
            }
        }
    </style>
"""

        if '</head>' in html_content:
            html_content = html_content.replace('</head>', mathjax_and_css + '</head>')
            Path(html_path).write_text(html_content, encoding='utf-8')
