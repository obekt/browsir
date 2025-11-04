# BrowSir API - Intelligent Web Content Extraction

A powerful REST API that uses **hybrid AI + local parsing** to extract clean content from any webpage, automatically handling popups, cookie banners, and dynamic content.

## 🎯 Hybrid Architecture

**Best of Both Worlds:**
- **OpenAI GPT-4o-mini**: Intelligently detects and dismisses popups (small task, ~50KB HTML)
- **BeautifulSoup**: Extracts content locally (no size limits, no API costs, instant)

This approach is **fast, cost-effective, and scalable** - AI where needed, local parsing for everything else!

## Features

- 🤖 **AI-Powered Popup Detection**: Uses OpenAI to find and dismiss consent forms
- 🚀 **Local Content Extraction**: BeautifulSoup parses HTML locally (no token limits!)
- 🌐 **Universal**: Works with any website - news, blogs, documentation, e-commerce
- 💰 **Cost-Effective**: OpenAI only for popups (~$0.001/request), extraction is FREE
- ⚡ **Fast**: No API calls for extraction, instant local parsing
- 📏 **No Size Limits**: Can process 2MB, 10MB, any size HTML
- 🎯 **Smart Clicking**: Multiple fallback strategies (CSS, text-based, JS, iframes)
- 🔒 **Multi-Language**: Detects consent forms in any language
- 🐳 **Docker Ready**: One-command deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd browserAPI
   ```

2. **Set your OpenAI API key**
   
   Edit the `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Start the service**
   ```bash
   docker-compose up -d
   ```

4. **Verify it's running**
   ```bash
   curl http://localhost:8000/health
   ```

That's it! The API is now running on `http://localhost:8000`

## Usage

### Extract Content from Any URL

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

### Response Format

```json
{
  "success": true,
  "data": {
    "title": "Article Title",
    "body": "Full article content with all paragraphs...",
    "images": ["https://example.com/image1.jpg"],
    "url": "https://example.com/article",
    "extracted_at": "2025-11-04T10:00:00.000000"
  },
  "error": null
}
```

## How It Works

### Hybrid Architecture

```
1. Load Page (Playwright)
   ↓
2. Detect Popups (OpenAI - analyzes 50KB HTML)
   ↓
3. Click Dismiss Buttons (Playwright - 5 strategies)
   ↓
4. Wait for Dynamic Content (8 seconds)
   ↓
5. Extract Content (BeautifulSoup - parses FULL HTML locally)
   ↓
6. Return Structured JSON
```

### Why Hybrid?

| Task | Tool | Why |
|------|------|-----|
| Popup Detection | OpenAI | Complex, varies by site, needs intelligence |
| Content Extraction | BeautifulSoup | Deterministic, no limits, free, fast |

**Result**: Best performance, lowest cost, no size limits!

## Use Cases

- **News Aggregation**: Extract articles from news sites
- **Content Monitoring**: Track changes on web pages
- **Research**: Collect data from multiple sources
- **SEO Analysis**: Extract content for analysis
- **Data Mining**: Gather information from dynamic websites
- **RSS Alternative**: Extract content from sites without RSS feeds
- **Price Monitoring**: Track product prices and availability
- **Documentation Scraping**: Collect technical documentation

## Configuration

All settings are in the `.env` file:

```bash
# Required - OpenAI API key (only for popup detection)
OPENAI_API_KEY=your-key-here

# Optional (with defaults)
OPENAI_MODEL=gpt-4o-mini          # AI model for popup detection
SELENIUM_TIMEOUT=30                # Page load timeout (seconds)
MAX_POPUP_RETRIES=3                # Max attempts to dismiss popups
CHROME_HEADLESS=true               # Run browser in background
LOG_LEVEL=INFO                     # Logging verbosity
```

## API Endpoints

### POST `/extract`

Extract content from a URL.

**Request:**
```json
{
  "url": "https://example.com/page"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "string",
    "body": "string",
    "images": ["string"],
    "url": "string",
    "extracted_at": "datetime"
  },
  "error": null
}
```

### GET `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T10:00:00.000000"
}
```

## Examples

### News Article
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bbc.com/news/article"}'
```

### Blog Post
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@author/post"}'
```

### Financial Data
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://finance.yahoo.com/quote/AAPL/"}'
```

### Product Page
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/product/B08N5WRWNW"}'
```

## Performance & Cost

### Speed
- **Popup detection**: 3-5 seconds (OpenAI API call)
- **Content extraction**: <1 second (local parsing)
- **Total**: 15-25 seconds (including page load and waits)

### Cost
- **Popup detection**: ~$0.001 per request (OpenAI)
- **Content extraction**: $0 (local BeautifulSoup)
- **Total**: ~$0.001 per extraction (99% cheaper than full AI extraction!)

### Scalability
- **No token limits**: Can process any size HTML
- **No rate limits**: Local extraction has no API limits
- **Concurrent requests**: Supports multiple simultaneous extractions
- **Memory**: ~500MB per container

## Architecture

### Technology Stack
- **FastAPI**: Modern async web framework
- **Playwright**: Browser automation with Chromium
- **OpenAI GPT-4o-mini**: AI for popup detection only
- **BeautifulSoup4**: Local HTML parsing for content extraction
- **Docker**: Containerized deployment
- **Python 3.11**: Runtime environment

### Why This Stack?
- **Playwright**: Better than Selenium for modern web apps
- **OpenAI**: Best for understanding complex popup patterns
- **BeautifulSoup**: Fast, reliable, no limits for content extraction
- **Hybrid approach**: Optimal balance of intelligence and efficiency

## Advantages Over Full AI Extraction

| Aspect | Full AI (Old) | Hybrid (New) |
|--------|---------------|--------------|
| Token Limits | 128K tokens | No limits |
| Max HTML Size | ~300KB | Unlimited |
| Cost per Request | ~$0.01 | ~$0.001 |
| Speed | Slower (2 API calls) | Faster (1 API call) |
| Reliability | AI hallucinations | Deterministic |
| Scalability | Rate limited | Unlimited |

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs -f

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Popups not being dismissed
- Check logs: `docker-compose logs | grep "Popup detection"`
- The AI should detect and click consent buttons automatically
- If issues persist, see `TESTING_GUIDE.md`

### Content extraction incomplete
- The system extracts from the entire HTML (no size limits)
- Check logs: `docker-compose logs | grep "HTML length"`
- Increase wait times in `app/main.py` if needed

### OpenAI API errors
- Verify your API key is correct in `.env`
- Check you have credits: https://platform.openai.com/usage
- Note: OpenAI is only used for popup detection, not extraction

## Development

### View Logs
```bash
docker-compose logs -f
```

### Restart Service
```bash
docker-compose restart
```

### Stop Service
```bash
docker-compose down
```

### Update Code
```bash
# After making changes
docker-compose down
docker-compose build
docker-compose up -d
```

## Documentation

- **README.md** (this file) - Overview and quick start
- **INSTALLATION.md** - Complete installation guide
- **QUICKSTART.md** - 5-minute setup
- **TESTING_GUIDE.md** - Testing and debugging
- **DYNAMIC_CONTENT_FIX.md** - Technical details
- **ARCHITECTURE.md** - System architecture

## Security

- API runs in isolated Docker container
- No data persistence (stateless)
- Browser runs in sandbox mode
- All requests are logged for monitoring
- `.env` file in `.gitignore` (API key not committed)

## Limitations

- Requires OpenAI API key for popup detection (paid service)
- Some sites may block automated access
- Very complex SPAs may need longer wait times
- Popup detection rate limited by OpenAI API quotas

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Changelog

### v2.0.0 (2025-11-04) - Hybrid Architecture
- **BREAKING**: Switched to hybrid AI + local parsing
- Added BeautifulSoup for local content extraction
- Removed token limits (can process any size HTML)
- 99% cost reduction for content extraction
- Faster extraction (no API call needed)
- More reliable (deterministic parsing)

### v1.0.0 (2025-11-04)
- Initial release
- AI-powered popup detection
- Multi-strategy button clicking
- Dynamic content support
- Docker deployment