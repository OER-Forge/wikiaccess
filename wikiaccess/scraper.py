"""
WikiAccess - DokuWiki HTTP Scraper and Converter

This module fetches content from DokuWiki via HTTP without requiring XML-RPC API.
Works with any DokuWiki instance by fetching the raw export format.

Part of WikiAccess: Transform DokuWiki into Accessible Documents
https://github.com/yourusername/wikiaccess
"""

import re
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
import time


class DokuWikiHTTPClient:
    """
    Fetch DokuWiki content via HTTP scraping
    No XML-RPC API required!
    """
    
    def __init__(self, base_url: str, username: Optional[str] = None, 
                 password: Optional[str] = None):
        """
        Initialize HTTP client for DokuWiki
        
        Args:
            base_url: Base URL of DokuWiki (e.g., 'https://wiki.example.com')
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DokuWiki-to-Word-Converter/1.0'
        })
        
        # Login if credentials provided
        if username and password:
            self._login(username, password)
    
    def _login(self, username: str, password: str) -> bool:
        """Login to DokuWiki"""
        login_url = f"{self.base_url}/doku.php?do=login"
        
        try:
            # Get login page to get sectok
            response = self.session.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find sectok (security token)
            sectok_input = soup.find('input', {'name': 'sectok'})
            sectok = sectok_input['value'] if sectok_input else ''
            
            # Submit login
            login_data = {
                'u': username,
                'p': password,
                'sectok': sectok,
                'do': 'login'
            }
            
            response = self.session.post(login_url, data=login_data)
            
            if 'Logged in as' in response.text or username in response.text:
                print(f"✓ Logged in as {username}")
                return True
            else:
                print(f"⚠ Login may have failed, continuing anyway...")
                return False
                
        except Exception as e:
            print(f"⚠ Login failed: {e}, continuing without authentication")
            return False
    
    def get_page_raw(self, page_id: str) -> Optional[str]:
        """
        Fetch raw DokuWiki syntax for a page
        
        Args:
            page_id: Page identifier (e.g., '183_notes:scalars_and_vectors')
        
        Returns:
            Raw DokuWiki syntax or None if failed
        """
        # Use the export_raw action to get raw wiki syntax
        url = f"{self.base_url}/doku.php?id={page_id}&do=export_raw"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            print(f"✓ Fetched page: {page_id}")
            return response.text
            
        except Exception as e:
            print(f"✗ Failed to fetch {page_id}: {e}")
            return None
    
    def get_page_from_url(self, url: str) -> Optional[Tuple[str, str]]:
        """
        Extract page ID from URL and fetch content
        
        Args:
            url: Full URL to DokuWiki page
        
        Returns:
            Tuple of (page_id, raw_content) or None
        """
        page_id = self.extract_page_id(url)
        if not page_id:
            return None
        
        content = self.get_page_raw(page_id)
        if content:
            return (page_id, content)
        
        return None
    
    def extract_page_id(self, url: str) -> Optional[str]:
        """
        Extract page ID from a DokuWiki URL
        
        Examples:
            https://wiki.com/doku.php?id=namespace:page -> namespace:page
            https://wiki.com/namespace/page -> namespace:page
        """
        parsed = urlparse(url)
        
        # Try query parameter
        if 'id=' in parsed.query:
            params = parse_qs(parsed.query)
            if 'id' in params:
                return params['id'][0]
        
        # Try path-based URL (some DokuWiki configs)
        path = parsed.path.strip('/')
        if path and path != 'doku.php':
            # Remove common prefixes
            path = path.replace('doku.php/', '')
            # Convert slashes to colons
            return path.replace('/', ':')
        
        return None
    
    def download_media(self, media_path: str, output_path: str) -> bool:
        """
        Download a media file from DokuWiki
        
        Args:
            media_path: Media path (e.g., 'namespace:image.png' or 'namespace/image.png')
            output_path: Local path to save file
        
        Returns:
            True if successful
        """
        # Convert to media path format
        media_path = media_path.replace('/', ':')
        
        # Try multiple URL patterns
        urls_to_try = [
            f"{self.base_url}/lib/exe/fetch.php?media={media_path}",
            f"{self.base_url}/lib/exe/fetch.php?media={media_path.replace(':', '/')}",
            f"{self.base_url}/_media/{media_path.replace(':', '/')}",
        ]
        
        for url in urls_to_try:
            try:
                response = self.session.get(url, timeout=10)
                
                # Check if we got actual media content
                content_type = response.headers.get('Content-Type', '')
                if response.status_code == 200 and ('image/' in content_type or 'application/' in content_type):
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✓ Downloaded: {media_path}")
                    return True
                    
            except Exception as e:
                continue
        
        print(f"⚠ Could not download: {media_path}")
        return False
    
    def get_youtube_info(self, video_id: str) -> Dict:
        """Get YouTube video information"""
        return {
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'thumbnail_hq': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
        }
    
    def download_youtube_thumbnail(self, video_id: str, output_path: str) -> bool:
        """Download YouTube video thumbnail"""
        info = self.get_youtube_info(video_id)
        
        # Try high quality first, fall back to standard
        for url in [info['thumbnail_url'], info['thumbnail_hq']]:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✓ Downloaded YouTube thumbnail: {video_id}")
                    return True
            except:
                continue
        
        print(f"⚠ Could not download thumbnail for: {video_id}")
        return False
    
    def resolve_internal_link(self, link: str, current_page: Optional[str] = None) -> str:
        """
        Resolve internal wiki link to full URL
        
        Args:
            link: Internal link (e.g., 'namespace:page' or ':page' or 'page')
            current_page: Current page ID for relative links
        
        Returns:
            Full URL
        """
        # Handle different link formats
        if link.startswith('http://') or link.startswith('https://'):
            return link  # Already a full URL
        
        # Convert to page ID format
        page_id = link.replace('/', ':')
        
        return f"{self.base_url}/doku.php?id={page_id}"
    
    def list_pages_from_index(self) -> List[str]:
        """
        Try to list pages from the public index
        Note: Only works if the index is publicly accessible
        """
        try:
            url = f"{self.base_url}/doku.php?do=index"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pages = []
            # Look for page links in the index
            for link in soup.find_all('a', {'class': 'wikilink1'}):
                href = link.get('href', '')
                if 'id=' in href:
                    page_id = parse_qs(urlparse(href).query).get('id', [None])[0]
                    if page_id:
                        pages.append(page_id)
            
            return list(set(pages))  # Remove duplicates
            
        except Exception as e:
            print(f"⚠ Could not fetch page index: {e}")
            return []


def test_http_client():
    """Test the HTTP client"""
    import sys
    
    print()
    print("=" * 70)
    print("DokuWiki HTTP Client Test")
    print("=" * 70)
    print()
    
    # Get URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter a DokuWiki page URL: ").strip()
    
    if not url:
        print("Error: URL is required")
        return
    
    # Ask for authentication
    print()
    auth_choice = input("Does your wiki require authentication? (y/n): ").strip().lower()
    
    username = None
    password = None
    
    if auth_choice == 'y':
        username = input("Username: ").strip()
        from getpass import getpass
        password = getpass("Password: ")
    
    print()
    print("Testing HTTP scraper...")
    print()
    
    # Extract base URL
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Find the wiki root (might be in subdirectory)
    path_parts = parsed.path.split('/')
    for i, part in enumerate(path_parts):
        if part == 'doku.php' or part == 'dokuwiki':
            base_url += '/' + '/'.join(path_parts[:i])
            break
    else:
        # No doku.php in path, try to find it
        if '/wikis/' in parsed.path:
            # Pattern like /wikis/pcubed/
            wiki_path = parsed.path.split('?')[0]
            if wiki_path.endswith('/doku.php'):
                wiki_path = wiki_path[:-10]
            base_url += wiki_path.rstrip('/')
    
    print(f"Base URL: {base_url}")
    print()
    
    # Create client
    client = DokuWikiHTTPClient(base_url, username, password)
    
    # Test 1: Extract page ID
    print("Test 1: Extracting page ID from URL...")
    page_id = client.extract_page_id(url)
    if page_id:
        print(f"  ✓ Page ID: {page_id}")
    else:
        print(f"  ✗ Could not extract page ID")
        return
    
    print()
    
    # Test 2: Fetch page content
    print("Test 2: Fetching raw page content...")
    content = client.get_page_raw(page_id)
    
    if content:
        lines = content.strip().split('\n')
        print(f"  ✓ Retrieved {len(content)} characters, {len(lines)} lines")
        print()
        print("  First 10 lines:")
        for line in lines[:10]:
            preview = line[:70] + "..." if len(line) > 70 else line
            print(f"    {preview}")
    else:
        print(f"  ✗ Failed to fetch content")
        return
    
    print()
    
    # Test 3: Extract media references
    print("Test 3: Extracting media references...")
    image_pattern = re.compile(r'\{\{\s*(.+?)\s*(?:\?(\d+))?\s*\}\}')
    images = []
    videos = []
    
    for match in image_pattern.finditer(content):
        path = match.group(1)
        if 'youtube>' in path:
            video_id = path.replace('youtube>', '').split('?')[0]
            videos.append(video_id)
        else:
            images.append(path)
    
    if images:
        print(f"  ✓ Found {len(images)} images:")
        for img in images[:5]:
            print(f"    - {img}")
        if len(images) > 5:
            print(f"    ... and {len(images) - 5} more")
    
    if videos:
        print(f"  ✓ Found {len(videos)} YouTube videos:")
        for vid in videos:
            print(f"    - {vid}")
    
    if not images and not videos:
        print("  (No media found in this page)")
    
    print()
    
    # Test 4: Extract internal links
    print("Test 4: Extracting internal links...")
    link_pattern = re.compile(r'\[\[([^|]+?)(?:\|([^]]+?))?\]\]')
    internal_links = []
    
    for match in link_pattern.finditer(content):
        target = match.group(1)
        if not target.startswith('http'):
            internal_links.append(target)
    
    if internal_links:
        print(f"  ✓ Found {len(internal_links)} internal links:")
        for link in internal_links[:5]:
            full_url = client.resolve_internal_link(link)
            print(f"    - {link} -> {full_url}")
        if len(internal_links) > 5:
            print(f"    ... and {len(internal_links) - 5} more")
    else:
        print("  (No internal links found)")
    
    print()
    print("=" * 70)
    print("✓ HTTP scraper is working!")
    print("=" * 70)
    print()
    print("You can now convert pages using this scraper.")
    print()


if __name__ == '__main__':
    test_http_client()
