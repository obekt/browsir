from playwright.async_api import async_playwright, Browser, Page
from typing import Optional
import logging

logger = logging.getLogger(__name__)



class BrowserService:
    """Service for browser automation using Playwright Async API"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.timeout = timeout * 1000  # Convert seconds to milliseconds for Playwright
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.headless = headless
        
    async def _init_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch Chromium browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Create context and page
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            logger.info("Playwright browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {str(e)}")
            raise RuntimeError(
                f"Could not initialize Playwright browser: {str(e)}"
            )
        
    async def load_page(self, url: str) -> str:
        """Load a page and return its HTML"""
        if not self.page:
            await self._init_browser()
            
        logger.info(f"Loading page: {url}")
        # Wait for network to be idle (all resources loaded including JS)
        await self.page.goto(url, wait_until='networkidle')
        
        # Wait additional time for any dynamic content/popups to appear
        await self.page.wait_for_timeout(3000)
        
        html = await self.page.content()
        logger.info(f"Page loaded, HTML length: {len(html)} bytes")
        return html
    
    async def click_element(self, selector: str, button_text: Optional[str] = None) -> bool:
        """Click an element by CSS selector with multiple fallback strategies"""
        try:
            if not self.page:
                logger.error("No page available for clicking")
                return False
            
            logger.info(f"Attempting to click element: {selector}" + (f" with text: {button_text}" if button_text else ""))
            
            # Strategy 1: Standard click
            try:
                await self.page.click(selector, timeout=5000)
                await self.page.wait_for_timeout(1000)
                logger.info(f"Successfully clicked (standard): {selector}")
                return True
            except Exception as e1:
                logger.debug(f"Standard click failed: {str(e1)}")
            
            # Strategy 2: Try text-based selector if button_text provided
            if button_text:
                try:
                    # Playwright text selector: button:has-text("Accept")
                    text_selector = f"button:has-text('{button_text}')"
                    await self.page.click(text_selector, timeout=5000)
                    await self.page.wait_for_timeout(1000)
                    logger.info(f"Successfully clicked (text): {text_selector}")
                    return True
                except Exception as e2:
                    logger.debug(f"Text-based click failed: {str(e2)}")
                    
                # Try with any clickable element containing text
                try:
                    text_selector = f":has-text('{button_text}')"
                    await self.page.click(text_selector, timeout=5000)
                    await self.page.wait_for_timeout(1000)
                    logger.info(f"Successfully clicked (any element with text): {text_selector}")
                    return True
                except Exception as e3:
                    logger.debug(f"Any element text click failed: {str(e3)}")
            
            # Strategy 3: Force click (bypass actionability checks)
            try:
                await self.page.click(selector, timeout=5000, force=True)
                await self.page.wait_for_timeout(1000)
                logger.info(f"Successfully clicked (force): {selector}")
                return True
            except Exception as e4:
                logger.debug(f"Force click failed: {str(e4)}")
            
            # Strategy 4: JavaScript click
            try:
                element = await self.page.query_selector(selector)
                if element:
                    await element.evaluate("el => el.click()")
                    await self.page.wait_for_timeout(1000)
                    logger.info(f"Successfully clicked (JS): {selector}")
                    return True
            except Exception as e5:
                logger.debug(f"JS click failed: {str(e5)}")
            
            # Strategy 5: Try finding in iframes
            try:
                frames = self.page.frames
                for frame in frames:
                    try:
                        element = await frame.query_selector(selector)
                        if element:
                            await element.click(timeout=5000)
                            await self.page.wait_for_timeout(1000)
                            logger.info(f"Successfully clicked in iframe: {selector}")
                            return True
                    except:
                        continue
            except Exception as e6:
                logger.debug(f"Iframe click failed: {str(e6)}")
            
            logger.warning(f"All click strategies failed for: {selector}")
            return False
            
        except Exception as e:
            logger.warning(f"Failed to click {selector}: {str(e)}")
            return False
    
    async def get_html(self) -> str:
        """Get current page HTML"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        return await self.page.content()
    
    async def close(self):
        """Close browser and clean up"""
        if self.page:
            await self.page.close()
            self.page = None
        if self.browser:
            logger.info("Closing browser")
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


