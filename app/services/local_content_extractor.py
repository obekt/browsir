from typing import Dict, List
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class LocalContentExtractor:
    """Extract content locally using BeautifulSoup - no AI needed, no token limits"""
    
    def extract_content(self, html: str, url: str) -> Dict:
        """
        Extract content from HTML using local parsing
        
        Returns:
            {
                "title": str,
                "body": str,
                "images": [str]
            }
        """
        try:
            logger.info("Extracting content locally with BeautifulSoup")
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract body content
            body = self._extract_body(soup)
            
            # Extract images
            images = self._extract_images(soup, url)
            
            logger.info(f"Local extraction successful: title='{title[:50]}...', body length={len(body)}")
            
            return {
                "title": title,
                "body": body,
                "images": images
            }
            
        except Exception as e:
            logger.error(f"Error in local content extraction: {str(e)}")
            return {"title": "", "body": "", "images": []}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try multiple strategies
        strategies = [
            lambda: soup.find('h1').get_text(strip=True) if soup.find('h1') else None,
            lambda: soup.find('title').get_text(strip=True) if soup.find('title') else None,
            lambda: soup.find('meta', property='og:title')['content'] if soup.find('meta', property='og:title') else None,
            lambda: soup.find('meta', attrs={'name': 'title'})['content'] if soup.find('meta', attrs={'name': 'title'}) else None,
        ]
        
        for strategy in strategies:
            try:
                title = strategy()
                if title:
                    return title
            except:
                continue
        
        return "Untitled"
    
    def _extract_body(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            element.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Strategy 1: Look for main/article tags
        for tag in ['main', 'article', '[role="main"]']:
            main_content = soup.select_one(tag)
            if main_content:
                break
        
        # Strategy 2: Look for common content containers
        if not main_content:
            for selector in ['#content', '#main-content', '.content', '.main-content', '.article-body']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
        
        # Strategy 3: Use body if nothing else found
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Extract text with structure
        text_parts = []
        
        # Get all text elements
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'div']):
            text = element.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short text
                # Add markdown formatting for headings
                if element.name in ['h1', 'h2', 'h3']:
                    text = f"\n\n**{text}**\n"
                elif element.name == 'li':
                    text = f"- {text}"
                
                text_parts.append(text)
        
        # Join and clean up
        body = '\n\n'.join(text_parts)
        
        # Clean up excessive whitespace
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = re.sub(r' {2,}', ' ', body)
        
        return body.strip()
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract image URLs"""
        images = []
        
        # Find all img tags
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # Skip small images (likely icons/logos)
                width = img.get('width')
                height = img.get('height')
                
                try:
                    if width and height:
                        if int(width) < 100 or int(height) < 100:
                            continue
                except:
                    pass
                
                # Make absolute URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    src = f"{parsed.scheme}://{parsed.netloc}{src}"
                elif not src.startswith('http'):
                    continue
                
                images.append(src)
        
        # Limit to reasonable number
        return images[:10]

