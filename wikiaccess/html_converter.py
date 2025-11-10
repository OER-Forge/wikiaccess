#!/usr/bin/env python3
"""
WikiAccess - HTML Converter

Generates WCAG 2.1 AA/AAA compliant HTML with:
- MathJax 3 for equations
- Semantic HTML5
- High contrast and dark mode support
- Embedded images and YouTube videos
- Simple, accessible CSS

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

from pathlib import Path
from typing import Optional, List, Tuple
from .scraper import DokuWikiHTTPClient
from .parser import DokuWikiParser
import re
import html as html_lib


class HTMLConverter:
    """Convert DokuWiki to accessible HTML"""
    
    def __init__(self, client: DokuWikiHTTPClient, output_dir: Optional[str] = None):
        self.client = client
        self.parser = DokuWikiParser()
        self.output_dir = Path(output_dir) if output_dir else Path('output/html')
        self.images_dir = self.output_dir / 'images'
        self.current_page_id = None
        self.image_count = 0
        self.video_count = 0
        self.equation_count = 0
        self.image_success = 0
        self.image_failed = 0
        self.video_success = 0
        self.video_failed = 0
        
    def convert_url(self, url: str, document_title: Optional[str] = None,
                   language: str = 'en') -> Tuple[str, dict]:
        """
        Convert DokuWiki page to HTML
        
        Returns:
            Tuple of (html_output_path, conversion_stats)
        """
        print(f"\n🌐 Converting to HTML: {url}")
        print("=" * 70)
        
        # Fetch page content
        result = self.client.get_page_from_url(url)
        if not result:
            print("✗ Failed to fetch page content")
            return None, {}
        
        page_id, content = result
        self.current_page_id = page_id
        
        # Generate title
        if document_title is None:
            document_title = page_id.replace('_', ' ').replace(':', ' - ').title()
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Reset counters
        self.image_count = 0
        self.video_count = 0
        self.equation_count = 0
        
        # Convert content to HTML
        html_content = self._generate_html(content, document_title, language)
        
        # Save HTML file
        output_path = self.output_dir / f"{page_id.replace(':', '_')}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        stats = {
            'images': self.image_count,
            'videos': self.video_count,
            'equations': self.equation_count,
            'images_success': self.image_success,
            'images_failed': self.image_failed,
            'videos_success': self.video_success,
            'videos_failed': self.video_failed
        }
        
        print(f"\n✓ HTML saved: {output_path}")
        print(f"  📊 Stats: {self.image_success}/{self.image_count} images, {self.video_success}/{self.video_count} videos, {self.equation_count} equations")
        
        return str(output_path), stats
    
    def _generate_html(self, content: str, title: str, language: str) -> str:
        """Generate complete HTML document"""
        
        # Parse DokuWiki content
        body_html = self._convert_content(content)
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_lib.escape(title)}</title>
    
    <!-- MathJax 3 for equations -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']],
                processEscapes: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        /* Base accessible styles - simple and clean */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            font-size: 18px;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            color: #1a1a1a;
            background: #ffffff;
        }}
        
        /* High contrast mode */
        @media (prefers-contrast: high) {{
            body {{
                color: #000000;
                background: #ffffff;
            }}
            a {{
                color: #0000ee;
                text-decoration: underline;
            }}
        }}
        
        /* Dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                color: #e0e0e0;
                background: #1a1a1a;
            }}
            a {{
                color: #58a6ff;
            }}
            img {{
                opacity: 0.9;
            }}
        }}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            line-height: 1.3;
        }}
        
        h1 {{ font-size: 2.5em; }}
        h2 {{ font-size: 2em; }}
        h3 {{ font-size: 1.5em; }}
        h4 {{ font-size: 1.25em; }}
        h5 {{ font-size: 1.1em; }}
        
        p {{
            margin-bottom: 1em;
        }}
        
        /* Links */
        a {{
            color: #0066cc;
            text-decoration: underline;
        }}
        
        a:hover {{
            text-decoration: none;
        }}
        
        a:focus {{
            outline: 3px solid #0066cc;
            outline-offset: 2px;
        }}
        
        /* Lists */
        ul, ol {{
            margin-left: 2em;
            margin-bottom: 1em;
        }}
        
        li {{
            margin-bottom: 0.5em;
        }}
        
        /* Images */
        figure {{
            margin: 1.5em 0;
            text-align: center;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        
        figcaption {{
            margin-top: 0.5em;
            font-style: italic;
            color: #666666;
        }}
        
        /* Videos */
        .video-container {{
            position: relative;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            height: 0;
            overflow: hidden;
            margin: 1.5em 0;
        }}
        
        .video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        /* Equations */
        .math-display {{
            margin: 1.5em 0;
            text-align: center;
            overflow-x: auto;
        }}
        
        /* Text formatting */
        strong {{ font-weight: 700; }}
        em {{ font-style: italic; }}
        
        /* Skip link for keyboard navigation */
        .skip-link {{
            position: absolute;
            top: -40px;
            left: 0;
            background: #0066cc;
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 100;
        }}
        
        .skip-link:focus {{
            top: 0;
        }}
    </style>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <main id="main-content" role="main">
        <h1>{html_lib.escape(title)}</h1>
        {body_html}
    </main>
    
    <footer role="contentinfo" style="margin-top: 3em; padding-top: 1em; border-top: 1px solid #ccc; font-size: 0.9em; color: #666;">
        <p>Generated from DokuWiki | <a href="#main-content">Back to top</a></p>
    </footer>
</body>
</html>"""
        
        return html
    
    def _convert_content(self, content: str) -> str:
        """Convert DokuWiki content to HTML body"""
        lines = content.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            parsed = self.parser.parse_line(line)
            
            if parsed['type'] == 'heading':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                level = parsed['level']
                text = self._process_inline(parsed['content'])
                html_lines.append(f'<h{level}>{text}</h{level}>')
            
            elif parsed['type'] == 'paragraph':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                text = self._process_inline(parsed['content'])
                if text.strip():
                    html_lines.append(f'<p>{text}</p>')
            
            elif parsed['type'] == 'list_item':
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                text = self._process_inline(parsed['content'])
                html_lines.append(f'<li>{text}</li>')
            
            elif parsed['type'] == 'image':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(self._process_image(parsed))
            
            elif parsed['type'] == 'youtube':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(self._process_youtube(parsed['video_id']))
            
            elif parsed['type'] == 'equation_block':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                self.equation_count += 1
                equation = html_lib.escape(parsed['content'])
                html_lines.append(f'<div class="math-display">$$\\displaystyle {equation}$$</div>')
            
            elif parsed['type'] == 'empty':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
        
        if in_list:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    def _process_inline(self, text: str) -> str:
        """Process inline formatting"""
        elements = self.parser.parse_inline_formatting(text)
        html_parts = []
        
        for elem_type, elem_data in elements:
            if elem_type == 'text':
                html_parts.append(html_lib.escape(elem_data['content']))
            elif elem_type == 'bold':
                inner = self._process_inline(elem_data['content'])
                html_parts.append(f'<strong>{inner}</strong>')
            elif elem_type == 'italic':
                inner = self._process_inline(elem_data['content'])
                html_parts.append(f'<em>{inner}</em>')
            elif elem_type == 'underline':
                inner = self._process_inline(elem_data['content'])
                html_parts.append(f'<u>{inner}</u>')
            elif elem_type == 'link':
                url = elem_data['url']
                if not url.startswith('http'):
                    url = self.client.resolve_internal_link(url, self.current_page_id)
                text = html_lib.escape(elem_data['text'])
                html_parts.append(f'<a href="{html_lib.escape(url)}">{text}</a>')
            elif elem_type == 'equation_inline':
                self.equation_count += 1
                eq = html_lib.escape(elem_data['content'])
                html_parts.append(f'\\({eq}\\)')
        
        return ''.join(html_parts)
    
    def _process_image(self, parsed: dict) -> str:
        """Process and embed image"""
        image_path = parsed['path']
        width = parsed.get('width')
        
        # Check for YouTube videos
        if 'youtube>' in image_path:
            video_id = image_path.replace('youtube>', '').split('?')[0].strip()
            return self._process_youtube(video_id)
        
        # Skip URL embeds
        if 'url>' in image_path or image_path.startswith('http'):
            return f'<p><em>[External content: {html_lib.escape(image_path)}]</em></p>'
        
        # Clean up image path - remove size params and alt text
        clean_path = image_path.split('|')[0].split('?')[0].strip()
        
        # Extract alt text if provided
        alt_text = ''
        if '|' in image_path:
            parts = image_path.split('|')
            if len(parts) > 1:
                alt_text = parts[1].strip()
        
        # Download image
        try:
            # Generate filename from clean path
            filename = Path(clean_path).name
            if not filename:
                filename = f"image_{self.image_count}.png"
            
            save_path = self.images_dir / filename
            
            # Download using client
            success = self.client.download_media(clean_path, str(save_path))
            
            if success:
                self.image_count += 1
                self.image_success += 1
                
                # Generate alt text if not provided
                if not alt_text:
                    alt_text = filename.replace('_', ' ').replace('-', ' ').rsplit('.', 1)[0]
                
                # Build HTML
                img_tag = f'<img src="images/{filename}" alt="{html_lib.escape(alt_text)}"'
                if width:
                    img_tag += f' style="max-width: {width}px;"'
                img_tag += ' loading="lazy">'
                
                return f'<figure>{img_tag}<figcaption>{html_lib.escape(alt_text)}</figcaption></figure>'
            else:
                self.image_count += 1
                self.image_failed += 1
            
        except Exception as e:
            self.image_count += 1
            self.image_failed += 1
            print(f"  ⚠ Image download failed: {clean_path} - {e}")
        
        return f'<p><em>Image: {html_lib.escape(clean_path)}</em></p>'
    
    def _process_youtube(self, video_id: str) -> str:
        """Embed YouTube video with iframe"""
        self.video_count += 1
        self.video_success += 1
        
        print(f"  ✓ Embedded video: {video_id}")
        
        return f'''<figure class="video-container">
    <iframe 
        width="560" 
        height="315" 
        src="https://www.youtube-nocookie.com/embed/{html_lib.escape(video_id)}" 
        title="YouTube video player" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
        loading="lazy">
    </iframe>
    <figcaption>Video: YouTube ID {html_lib.escape(video_id)}</figcaption>
</figure>'''
