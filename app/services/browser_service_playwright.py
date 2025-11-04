from playwright.sync_api import sync_playwright, Browser, Page
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BrowserService:
    """Service for browser automation using Playwright"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.timeout = timeout  # Playwright uses milliseconds
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.headless = headless
        
    def _init_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            self.page = self.browser.new_page(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            self.page.set_default_timeout(self.timeout)
            logger.info("Playwright browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {str(e)}")
            raise RuntimeError(
                "Could not initialize Playwright browser. "
                "Please run: playwright install chromium"
            )
        
    def load_page(self, url: str) -> str:
        """Load a page and return its HTML"""
        if not self.page:
            self._init_browser()
            
        logger.info(f"Loading page: {url}")
        self.page.goto(url, wait_until='domcontentloaded')
        
        # Wait a bit for dynamic content
        self.page.wait_for_timeout(2000)
        
        return self.page.content()
    
    def click_element(self, selector: str) -> bool:
        """Click an element by CSS selector"""
        try:
            logger.info(f"Attempting to click element: {selector}")
            self.page.click(selector, timeout=5000)
            
            # Wait for potential page changes
            self.page.wait_for_timeout(1000)
            
            logger.info(f"Successfully clicked: {selector}")
            return True
        except Exception as e:
            logger.warning(f"Failed to click {selector}: {str(e)}")
            return False
    
    def get_html(self) -> str:
        """Get current page HTML"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        return self.page.content()
    
    def close(self):
        """Close browser and clean up"""
        if self.page:
            self.page.close()
            self.page = None
        if self.browser:
            logger.info("Closing browser")
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


