# Testing Guide - BrowSir API

## Overview
The BrowSir API uses a **hybrid AI + local parsing architecture** to extract content from any webpage:
- **OpenAI**: Intelligently detects and dismisses popups (small task, ~$0.001/request)
- **BeautifulSoup**: Extracts content locally (free, no limits, instant!)

This approach is fast, cost-effective, and can handle any HTML size.

## Quick Test

### 1. Start the Service
```bash
docker-compose up -d
```

### 2. Test with a Simple Page
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 3. Check Logs
```bash
docker-compose logs -f
```

## How It Works

### Extraction Flow
```
1. Load Page → 2. Detect Popups → 3. Click Buttons → 4. Wait for Content → 5. Extract & Return
```

### Key Features

#### 1. **Hybrid Architecture** 🎯
- **OpenAI**: Popup detection only (intelligent, small task)
- **BeautifulSoup**: Content extraction (local, free, no limits!)
- **Result**: 99% cost reduction, unlimited HTML size

#### 2. **Intelligent Popup Detection** (OpenAI)
- AI analyzes first 50KB of HTML
- Detects consent forms in any language
- Returns exact CSS selectors and button text
- Cost: ~$0.001 per request

#### 3. **Multi-Strategy Clicking** (Playwright)
The system tries 5 different strategies to click buttons:
1. **Standard click**: Normal browser click
2. **Text-based click**: Finds button by text (e.g., "Accept All")
3. **Force click**: Bypasses visibility checks
4. **JavaScript click**: Direct DOM manipulation
5. **Iframe search**: Looks inside iframes

#### 4. **Local Content Extraction** (BeautifulSoup)
- Parses entire HTML locally (no size limits!)
- Extracts title, body, images
- No API costs
- Instant processing
- Deterministic (no AI hallucinations)

#### 5. **Dynamic Content Handling**
- Waits for JavaScript to load content
- Handles async data fetching
- Captures fully rendered pages

## Test Cases

### 1. News Article
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bbc.com/news"}'
```
**Expected**: Article headlines, summaries, and content

### 2. Blog Post
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/@username/post-title"}'
```
**Expected**: Full blog post with title and body

### 3. Documentation Page
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org/3/tutorial/"}'
```
**Expected**: Documentation content and code examples

### 4. E-commerce Product
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/product/B08N5WRWNW"}'
```
**Expected**: Product title, description, and details

### 5. Dynamic Content Page
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://finance.yahoo.com/quote/AAPL/"}'
```
**Expected**: Stock data, news, and financial information

## What to Look For in Logs

### Success Indicators
```
✅ Playwright browser initialized successfully
✅ Page loaded, HTML length: 95000 bytes
✅ Found button with selector: button.accept-all, text: 'Accept All', confidence: 0.9
✅ Successfully clicked (text): button:has-text('Accept All')
✅ Final HTML length: 250000 bytes (dynamic content loaded)
✅ Content extraction successful: title='Page Title...'
```

### Failure Indicators
```
❌ All click strategies failed for: button[role='button']
❌ Could not click any popup elements
❌ Final HTML length: 90000 bytes (content didn't load)
❌ No article content found on the page
```

## Expected Behavior

### Successful Extraction
1. ✅ Browser loads page (5-8 seconds)
2. ✅ AI detects consent form
3. ✅ Clicks dismiss button
4. ✅ Waits for dynamic content (8 seconds)
5. ✅ Extracts full content
6. ✅ Returns structured JSON

### Response Format
```json
{
  "success": true,
  "data": {
    "title": "Article or Page Title",
    "body": "Complete content with all paragraphs, data, and information...",
    "images": ["https://example.com/image1.jpg"],
    "url": "https://example.com/page",
    "extracted_at": "2025-11-04T10:00:00.000000"
  },
  "error": null
}
```

## Debugging

### Issue: Minimal Content Returned

**Symptoms:**
- Response has title but very short body
- Missing expected content

**Solutions:**
1. Check HTML size in logs:
   ```bash
   docker-compose logs | grep "HTML length"
   ```
   - Initial: ~90KB (skeleton)
   - Final: Should be 200KB+ (with content)

2. Increase wait times if needed:
   Edit `app/main.py`:
   ```python
   await asyncio.sleep(7)  # Increase from 5 to 7
   ```

### Issue: Popups Not Dismissed

**Symptoms:**
- Logs show "All click strategies failed"
- Content is from consent page

**Solutions:**
1. Check what AI detected:
   ```bash
   docker-compose logs | grep "Popup detection result"
   ```

2. Verify button text:
   ```bash
   docker-compose logs | grep "button_text"
   ```

3. The system should automatically handle this, but if issues persist:
   - Check if site uses unusual consent management
   - May need to add specific selectors

### Issue: Service Won't Start

**Solutions:**
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: OpenAI API Errors

**Solutions:**
1. Verify API key in `.env`:
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. Check OpenAI account:
   - Visit: https://platform.openai.com/usage
   - Ensure you have credits
   - Verify API key is active

## Performance Metrics

### Timing Breakdown
| Step | Duration | Purpose |
|------|----------|---------|
| Page load | 5-8s | Initial HTML + network idle |
| Popup detection | 3-4s | AI analyzes HTML |
| Click consent | 1s | Dismiss overlay |
| Post-click wait | 5s | Page re-initialization |
| Content load wait | 3s | Dynamic content loading |
| Content extraction | 3-5s | AI extracts content |
| **Total** | **20-26s** | Complete extraction |

### Resource Usage
- **Memory**: ~500MB per container
- **CPU**: Moderate during extraction
- **Network**: Depends on page size
- **Disk**: Minimal (stateless)

## Advanced Configuration

### Increase Wait Times
For very slow pages, edit `app/main.py`:

```python
# After clicking popups (line ~121)
await asyncio.sleep(7)  # Increase from 5 to 7

# Before extraction (line ~132)
await asyncio.sleep(5)  # Increase from 3 to 5
```

### Adjust HTML Limit
For pages with lots of content, edit `app/services/content_extractor.py`:

```python
html_sample = html[:200000]  # Increase from 150KB to 200KB
```

### Lower Confidence Threshold
For more aggressive popup clicking, edit `app/main.py`:

```python
if confidence > 0.2 and selector:  # Lower from 0.3 to 0.2
```

### Change OpenAI Model
Edit `.env`:
```bash
OPENAI_MODEL=gpt-4o  # Use more powerful model
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### View Real-time Logs
```bash
docker-compose logs -f
```

### Check Container Status
```bash
docker-compose ps
```

### Restart Service
```bash
docker-compose restart
```

## Best Practices

1. **Test with simple pages first** before complex ones
2. **Monitor logs** to understand what's happening
3. **Adjust wait times** based on page complexity
4. **Use appropriate OpenAI model** for your needs
5. **Set reasonable timeouts** to avoid hanging

## Common Patterns

### News Sites
- Usually have cookie banners
- Content loads quickly
- Standard wait times work well

### Financial Sites
- Complex consent forms
- Heavy JavaScript
- May need longer wait times

### E-commerce Sites
- Product data loads dynamically
- Images load separately
- Standard wait times usually sufficient

### Documentation Sites
- Usually no popups
- Static content
- Fast extraction

## Troubleshooting Checklist

- [ ] Service is running: `docker-compose ps`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] OpenAI API key is set in `.env`
- [ ] Logs show browser initialized
- [ ] Logs show page loaded
- [ ] HTML size increases after waiting
- [ ] Content extraction completes
- [ ] Response contains expected data

## Getting Help

If issues persist:
1. Check all logs: `docker-compose logs`
2. Verify configuration in `.env`
3. Test with a simple page first
4. Review `DYNAMIC_CONTENT_FIX.md` for details
5. Open an issue with logs and URL being tested