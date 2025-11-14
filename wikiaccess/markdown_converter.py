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
from pathlib import Path
from typing import Optional, Tuple, Dict
from .scraper import DokuWikiHTTPClient
from .parser import DokuWikiParser


class MarkdownConverter:
    """Convert DokuWiki content to Markdown, then to HTML/DOCX via Pandoc"""
    
    def __init__(self, client: DokuWikiHTTPClient, output_dir: Optional[str] = None):
        self.client = client
        self.parser = DokuWikiParser()
        self.output_dir = Path(output_dir) if output_dir else Path('output')
        self.images_dir = self.output_dir / 'images'
        self.current_page_id = None
        self.image_count = 0
        self.image_success = 0
        self.image_failed = 0
        
        # Check if pandoc is installed
        if not shutil.which('pandoc'):
            raise RuntimeError("Pandoc is not installed. Install it with: brew install pandoc (macOS) or apt-get install pandoc (Linux)")
    
    def convert_url(self, url: str, document_title: Optional[str] = None) -> Tuple[str, str, Dict]:
        """
        Convert DokuWiki URL to Markdown, then to HTML and DOCX
        
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
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert DokuWiki to Markdown
        markdown = self._convert_to_markdown(content, document_title)
        
        # Save markdown
        md_path = self.output_dir / f"{page_id.replace(':', '_')}.md"
        md_path.write_text(markdown, encoding='utf-8')
        print(f"✓ Markdown generated: {md_path}")
        
        # Convert Markdown to HTML
        html_path = self.output_dir / 'html' / f"{page_id.replace(':', '_')}.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        self._pandoc_convert(str(md_path), str(html_path), 'html')
        
        # Convert Markdown to DOCX
        docx_path = self.output_dir / 'docx' / f"{page_id.replace(':', '_')}.docx"
        docx_path.parent.mkdir(parents=True, exist_ok=True)
        self._pandoc_convert(str(md_path), str(docx_path), 'docx')
        
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
        """Download image and return Markdown reference"""
        image_path = parsed['path']
        width = parsed.get('width')
        
        # Check for YouTube videos
        if 'youtube>' in image_path:
            video_id = image_path.replace('youtube>', '').split('?')[0].strip()
            return f"![Video: {video_id}](https://www.youtube.com/watch?v={video_id})\n"
        
        # Skip URL embeds
        if 'url>' in image_path or image_path.startswith('http'):
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
            
            # Download using client
            success = self.client.download_media(clean_path, str(save_path))
            
            self.image_count += 1
            
            if success:
                self.image_success += 1
                
                # Generate alt text if not provided
                if not alt_text:
                    alt_text = filename.replace('_', ' ').replace('-', ' ').rsplit('.', 1)[0]
                
                # Return Markdown image reference
                return f"![{alt_text}](images/{filename})\n"
            else:
                self.image_failed += 1
                return f"[Image: {clean_path}]\n"
        
        except Exception as e:
            self.image_count += 1
            self.image_failed += 1
            print(f"  ⚠ Image download failed: {clean_path} - {e}")
            return f"[Image: {clean_path}]\n"
    
    def _pandoc_convert(self, md_path: str, output_path: str, format_type: str):
        """
        Use Pandoc to convert Markdown to target format
        
        Args:
            md_path: Path to markdown file
            output_path: Path to save output
            format_type: 'html' or 'docx'
        """
        try:
            if format_type == 'html':
                # HTML with embedded CSS for accessibility
                cmd = [
                    'pandoc',
                    md_path,
                    '-o', output_path,
                    '--from', 'markdown',
                    '--to', 'html5',
                    '--standalone',
                    '--css', '-',  # Will add CSS below
                    '--metadata', 'title=WikiAccess',
                    '--variable', 'lang=en'
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Enhance HTML with accessible CSS
                self._enhance_html_accessibility(output_path)
                
            elif format_type == 'docx':
                # DOCX with language metadata
                cmd = [
                    'pandoc',
                    md_path,
                    '-o', output_path,
                    '--from', 'markdown',
                    '--to', 'docx',
                    '--metadata', 'lang=en'
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
        """Add accessibility CSS to generated HTML"""
        html_content = Path(html_path).read_text(encoding='utf-8')
        
        # Insert CSS before closing </head>
        css = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            font-size: 18px;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: #1a1a1a;
            background: #ffffff;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            line-height: 1.3;
        }
        
        a {
            color: #0066cc;
            text-decoration: underline;
        }
        
        a:focus {
            outline: 3px solid #0066cc;
            outline-offset: 2px;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em 0;
        }
        
        figure {
            text-align: center;
            margin: 1.5em 0;
        }
        
        figcaption {
            font-style: italic;
            color: #666;
            margin-top: 0.5em;
        }
        
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        pre {
            background: #f5f5f5;
            padding: 1em;
            border-left: 4px solid #0066cc;
            overflow-x: auto;
        }
        
        @media (prefers-color-scheme: dark) {
            body {
                color: #e0e0e0;
                background: #1a1a1a;
            }
            code {
                background: #333;
            }
            pre {
                background: #333;
            }
        }
        
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #0066cc;
            color: white;
            padding: 8px;
            text-decoration: none;
        }
        
        .skip-link:focus {
            top: 0;
        }
    </style>
"""
        
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', css + '</head>')
            Path(html_path).write_text(html_content, encoding='utf-8')
