from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

from app.config import get_settings
from app.models.request import ExtractRequest
from app.models.response import ExtractResponse, ArticleContent
from app.services.browser_service import BrowserService
from app.services.popup_detector import PopupDetector
from app.services.local_content_extractor import LocalContentExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load and validate settings at startup
try:
    settings = get_settings()
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error("=" * 80)
    logger.error("FATAL ERROR: Failed to load configuration")
    logger.error("=" * 80)
    logger.error(f"Error: {str(e)}")
    logger.error("")
    logger.error("Please ensure your .env file contains a valid OPENAI_API_KEY.")
    logger.error("Get your API key from: https://platform.openai.com/api-keys")
    logger.error("")
    logger.error("Example .env file:")
    logger.error("  OPENAI_API_KEY=sk-proj-...")
    logger.error("=" * 80)
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting BrowSir API service")
    
    # Validate OpenAI API key at startup
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        # Make a minimal API call to validate the key
        logger.info("Validating OpenAI API key...")
        client.models.list()
        logger.info("✓ OpenAI API key is valid")
    except Exception as e:
        logger.error("=" * 80)
        logger.error("FATAL ERROR: Invalid OpenAI API key")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}")
        logger.error("")
        logger.error("Please set a valid OPENAI_API_KEY in your .env file.")
        logger.error("Get your API key from: https://platform.openai.com/api-keys")
        logger.error("")
        logger.error("Example .env file:")
        logger.error("  OPENAI_API_KEY=sk-proj-...")
        logger.error("=" * 80)
        # Exit immediately to prevent restart loop
        sys.exit(1)
    
    yield
    logger.info("Shutting down BrowSir API service")


app = FastAPI(
    title="BrowSir API",
    description="Hybrid AI + local parsing for intelligent web content extraction. Uses OpenAI for popup detection and BeautifulSoup for content extraction (no token limits!).",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/extract", response_model=ExtractResponse)
async def extract_content(request: ExtractRequest):
    """
    Extract article content from a URL using hybrid AI + local parsing
    
    This endpoint:
    1. Loads the URL using Playwright (browser automation)
    2. Uses OpenAI to detect and dismiss popups/cookie banners (AI for intelligence)
    3. Waits for dynamic content to load (JavaScript execution)
    4. Extracts content using BeautifulSoup (local parsing, no token limits!)
    5. Returns structured content
    
    Benefits of hybrid approach:
    - OpenAI only for popup detection (~$0.001 per request)
    - Content extraction is FREE (local BeautifulSoup parsing)
    - No size limits (can process any HTML size)
    - Fast and reliable
    """
    url = str(request.url)
    logger.info(f"Processing extraction request for: {url}")
    
    browser = None
    try:
        # Initialize services
        browser = BrowserService(
            headless=settings.chrome_headless,
            timeout=settings.selenium_timeout
        )
        popup_detector = PopupDetector(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
        content_extractor = LocalContentExtractor()
        
        # Load initial page
        html = await browser.load_page(url)
        
        # Handle popups (max retries)
        for attempt in range(settings.max_popup_retries):
            logger.info(f"Popup detection attempt {attempt + 1}/{settings.max_popup_retries}")
            
            # Call OpenAI to detect popups (synchronous call)
            popup_result = popup_detector.detect_popups(html)
            logger.info(f"Popup detection result: {popup_result}")
            
            if not popup_result.get("popups_found", False):
                logger.info("No popups detected")
                break
                
            # Try to click dismiss buttons
            elements = popup_result.get("elements", [])
            clicked_any = False
            
            for element in elements:
                selector = element.get("selector")
                confidence = element.get("confidence", 0)
                element_type = element.get("type", "unknown")
                button_text = element.get("button_text", "")
                
                logger.info(f"Found {element_type} with selector: {selector}, text: '{button_text}', confidence: {confidence}")
                
                # Try clicking even with lower confidence for consent forms
                if confidence > 0.3 and selector:
                    if await browser.click_element(selector, button_text):
                        clicked_any = True
                        logger.info(f"Successfully clicked {element_type}")
                        break  # Stop after first successful click
                        
            if clicked_any:
                # Wait for page to update and dynamic content to load after clicking
                import asyncio
                await asyncio.sleep(5)  # Increased from 2 to 5 seconds
                # Get updated HTML after clicking
                html = await browser.get_html()
                logger.info("Got updated HTML after clicking popups")
            else:
                logger.warning("Could not click any popup elements")
                break
        
        # Wait additional time for dynamic content to fully load
        import asyncio
        await asyncio.sleep(3)
        
        # Extract content from final page state using local parser
        final_html = await browser.get_html()
        logger.info(f"Final HTML length: {len(final_html)} bytes")
        logger.info("Extracting content locally (no AI, no token limits)...")
        content = content_extractor.extract_content(final_html, url)
        logger.info(f"Content extraction result: title='{content.get('title', '')[:50]}...'")
        
        # Validate extracted content
        if not content.get("title") and not content.get("body"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No article content found on the page"
            )
        
        # Build response
        article = ArticleContent(
            title=content.get("title", ""),
            body=content.get("body", ""),
            images=content.get("images", []),
            url=url,
            extracted_at=datetime.utcnow()
        )
        
        logger.info(f"Successfully extracted content from: {url}")
        return ExtractResponse(success=True, data=article)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract content: {str(e)}"
        )
    finally:
        if browser:
            await browser.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)


