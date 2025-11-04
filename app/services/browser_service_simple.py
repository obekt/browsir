import httpx
from bs4 import BeautifulSoup
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BrowserService:
    """Simple HTTP-based browser service using httpx and BeautifulSoup"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        self.current_html: str = ""
        
    async def _init_client(self):
        """Initialize HTTP client"""
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            )
        
    async def load_page(self, url: str) -> str:
        """Load a page and return its HTML"""
        await self._init_client()
            
        logger.info(f"Loading page: {url}")
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            self.current_html = response.text
            logger.info(f"Successfully loaded page: {len(self.current_html)} bytes")
            return self.current_html
        except Exception as e:
            logger.error(f"Failed to load page: {str(e)}")
            raise RuntimeError(f"Failed to load page: {str(e)}")
    
    async def click_element(self, selector: str) -> bool:
        """
        Simulate clicking an element by removing it from HTML
        (For popup dismissal, we just remove the popup from HTML)
        """
        try:
            logger.info(f"Simulating click on element: {selector}")
            soup = BeautifulSoup(self.current_html, 'html.parser')
            
            # Try to find and remove the element
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    element.decompose()
                self.current_html = str(soup)
                logger.info(f"Removed {len(elements)} element(s) matching: {selector}")
                return True
            else:
                logger.warning(f"No elements found matching: {selector}")
                return False
        except Exception as e:
            logger.warning(f"Failed to process selector {selector}: {str(e)}")
            return False
    
    async def get_html(self) -> str:
        """Get current page HTML"""
        return self.current_html
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            logger.info("Closing HTTP client")
            await self.client.aclose()
            self.client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


