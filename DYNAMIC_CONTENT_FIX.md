# Dynamic Content Loading - Technical Details

## Overview

Modern websites load content dynamically using JavaScript after the initial HTML loads. This document explains how the BrowSir API handles this challenge using a **hybrid AI + local parsing architecture**.

## Hybrid Architecture

Our system uses a two-stage approach:

1. **OpenAI (Popup Detection)**: Analyzes first 50KB of HTML to detect consent forms
   - Cost: ~$0.001 per request
   - Fast, intelligent, language-agnostic

2. **BeautifulSoup (Content Extraction)**: Parses entire HTML locally
   - No size limits (handles 1MB+ HTML)
   - Free, instant, deterministic
   - No API costs or token limits

**Result**: 99% cost reduction, unlimited HTML size, faster processing

## The Problem

### Traditional Web Scraping
```
Load HTML → Extract Content → Done
```
**Issue**: Only captures the initial skeleton, misses JavaScript-loaded content.

### Modern Websites
```
Load HTML Skeleton → Execute JavaScript → Fetch Data from APIs → Render Content
```
**Challenge**: Content appears seconds after the page "loads".

## Real-World Example

### What Happens:
1. **Initial Load (t=0s)**: Browser receives minimal HTML
   ```html
   <div id="content">Loading...</div>
   <script src="app.js"></script>
   ```

2. **JavaScript Execution (t=1-3s)**: Framework initializes
   ```javascript
   // React/Vue/Angular starts
   fetch('/api/data').then(data => render(data))
   ```

3. **Content Appears (t=3-8s)**: Data fetched and rendered
   ```html
   <div id="content">
     <h1>Article Title</h1>
     <p>Full content here...</p>
   </div>
   ```

### The Challenge
If we extract at t=0s, we only get "Loading..."
We need to wait until t=8s to get the actual content.

## Our Solution

### Multi-Stage Waiting Strategy

```
Load Page → Wait for Network Idle → Detect Popups → Click Consent → 
Wait 5s → Wait 3s More → Extract Content
```

### Implementation

#### 1. Initial Page Load (`app/services/browser_service.py`)
```python
await self.page.goto(url, wait_until='networkidle')
await self.page.wait_for_timeout(3000)  # 3 seconds
```
**Purpose**: 
- `networkidle`: Wait until no network requests for 500ms
- `3000ms`: Additional time for popups/overlays to appear

#### 2. Post-Consent Wait (`app/main.py`)
```python
if clicked_any:
    await asyncio.sleep(5)  # 5 seconds
    html = await browser.get_html()
```
**Purpose**: After dismissing consent, page re-initializes and loads content

#### 3. Pre-Extraction Wait (`app/main.py`)
```python
await asyncio.sleep(3)  # 3 seconds
final_html = await browser.get_html()
```
**Purpose**: Final wait for any remaining async content

### Total Wait Time: ~8 seconds
- Post-consent: 5s
- Pre-extraction: 3s
- **Result**: Captures fully loaded dynamic content

## Why This Works

### Modern Web Architecture

#### Single Page Applications (SPAs)
- React, Vue, Angular apps
- Initial HTML is minimal
- JavaScript builds the entire page
- Data fetched from APIs

#### Progressive Enhancement
- Basic HTML loads first
- JavaScript enhances with dynamic features
- Content streams in progressively

#### Lazy Loading
- Images load on scroll
- Content loads on demand
- Infinite scroll patterns

### Our Approach Handles All These

1. **Network Idle**: Ensures initial resources loaded
2. **Fixed Waits**: Gives JavaScript time to execute
3. **Multiple Captures**: Gets HTML at different stages
4. **AI Extraction**: Filters out loading states and placeholders

## Timing Breakdown

| Stage | Time | What's Happening | Cost |
|-------|------|------------------|------|
| Initial Load | 5-8s | HTML + CSS + JS bundles | Free |
| Network Idle | +0.5s | All resources downloaded | Free |
| Popup Wait | +3s | Overlays appear | Free |
| **Popup Detection (OpenAI)** | **+1-2s** | **AI analyzes first 50KB** | **~$0.001** |
| Click Consent | +1s | Dismiss overlay | Free |
| **Post-Click Wait** | **+5s** | **Page re-initializes** | Free |
| **Pre-Extract Wait** | **+3s** | **Dynamic content loads** | Free |
| **Content Extraction (BeautifulSoup)** | **<100ms** | **Local HTML parsing** | **Free** |
| **Total** | **~18-20s** | **Complete extraction** | **~$0.001** |

### Key Improvements in Hybrid Architecture
- **Faster**: BeautifulSoup extraction is instant (<100ms vs 4s with AI)
- **Cheaper**: 99% cost reduction (~$0.001 vs ~$0.10 per request)
- **Unlimited**: No HTML size limits (handles 1MB+ files)
- **Reliable**: Deterministic parsing, no AI hallucinations

## Content Types and Wait Times

### Static Sites (Blogs, Documentation)
- **Wait Time**: 3-5s sufficient
- **Why**: Content in initial HTML
- **Example**: Personal blogs, GitHub Pages

### News Sites
- **Wait Time**: 5-8s recommended
- **Why**: Articles load quickly, but ads/widgets take time
- **Example**: BBC, CNN, The Guardian

### Financial Sites
- **Wait Time**: 8-12s recommended
- **Why**: Real-time data, charts, multiple API calls
- **Example**: Yahoo Finance, Bloomberg, Trading platforms

### E-commerce Sites
- **Wait Time**: 5-8s sufficient
- **Why**: Product data loads fast, images lazy-load
- **Example**: Amazon, eBay, Shopify stores

### Heavy SPAs
- **Wait Time**: 10-15s may be needed
- **Why**: Complex frameworks, multiple data sources
- **Example**: Gmail, Notion, Figma

## Configuration

### Adjust Wait Times

Edit `app/main.py`:

```python
# After clicking popups (line ~121)
await asyncio.sleep(5)  # Increase for slower sites

# Before extraction (line ~132)
await asyncio.sleep(3)  # Increase for heavy JavaScript
```

### Recommendations by Site Type

```python
# Static sites
await asyncio.sleep(2)  # Post-click
await asyncio.sleep(1)  # Pre-extract

# News sites (default)
await asyncio.sleep(5)  # Post-click
await asyncio.sleep(3)  # Pre-extract

# Financial sites
await asyncio.sleep(7)  # Post-click
await asyncio.sleep(5)  # Pre-extract

# Heavy SPAs
await asyncio.sleep(10)  # Post-click
await asyncio.sleep(5)  # Pre-extract
```

## Alternative Approaches

### 1. Element-Based Waiting
Wait for specific elements to appear:

```python
# Wait for main content
await page.wait_for_selector('.article-body', timeout=10000)

# Wait for data to load
await page.wait_for_selector('.price-loaded', timeout=10000)
```

**Pros**: More precise, faster when element appears
**Cons**: Need to know selectors in advance, site-specific

### 2. Network Monitoring
Wait until specific API calls complete:

```python
# Wait for API response
await page.wait_for_response(
    lambda response: 'api/content' in response.url
)
```

**Pros**: Waits for actual data
**Cons**: Need to know API endpoints, complex to implement

### 3. Scroll-Based Loading
Scroll to trigger lazy loading:

```python
# Scroll to bottom
await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
await asyncio.sleep(2)
```

**Pros**: Loads more content
**Cons**: Slower, may trigger infinite scroll

### 4. Screenshot Comparison
Compare screenshots to detect changes:

```python
before = await page.screenshot()
await asyncio.sleep(2)
after = await page.screenshot()
# If different, content changed
```

**Pros**: Visual verification
**Cons**: Computationally expensive, false positives

## Why We Use Fixed Waits

### Advantages
1. **Simple**: Easy to understand and configure
2. **Reliable**: Works for most sites
3. **Predictable**: Consistent timing
4. **Generic**: No site-specific code needed

### Trade-offs
1. **Not Optimal**: May wait longer than needed
2. **Not Adaptive**: Same wait for all sites
3. **Performance**: Could be faster with smart waiting

### Future Improvements
- Adaptive wait times based on site type
- Element-based waiting for known patterns
- Network monitoring for API calls
- Hybrid approach combining multiple strategies

## Debugging Dynamic Content

### Check HTML Size
```bash
docker-compose logs | grep "HTML length"
```

**What to look for:**
- Initial: ~50-100KB (skeleton)
- Final: 200KB+ (with content)
- If final is still small, increase wait times

### Verify Content Loaded
```bash
docker-compose logs | grep "Content extraction"
```

**What to look for:**
- Title should be specific, not generic
- Body should be substantial, not just metadata
- If minimal, content didn't load yet

### Test Wait Times
Try different wait times to find optimal:

```python
# Test with 3s
await asyncio.sleep(3)

# Test with 5s
await asyncio.sleep(5)

# Test with 10s
await asyncio.sleep(10)
```

Compare HTML sizes and extracted content quality.

## Performance Optimization

### Balance Speed vs Completeness

**Fast (10s total)**
```python
await asyncio.sleep(3)  # Post-click
await asyncio.sleep(2)  # Pre-extract
```
- Good for: Static sites, simple pages
- Risk: May miss some dynamic content

**Balanced (15s total) - Current Default**
```python
await asyncio.sleep(5)  # Post-click
await asyncio.sleep(3)  # Pre-extract
```
- Good for: Most sites, news, blogs
- Risk: Minimal, works for 90% of sites

**Complete (20s total)**
```python
await asyncio.sleep(10)  # Post-click
await asyncio.sleep(5)  # Pre-extract
```
- Good for: Financial sites, heavy SPAs
- Risk: Slower, but captures everything

### Concurrent Requests
The service supports multiple simultaneous extractions:
- Each request gets its own browser instance
- No shared state between requests
- Limited by system resources (CPU, memory)

## Monitoring

### Key Metrics to Track

1. **HTML Size Growth**
   - Initial vs Final HTML size
   - Should increase significantly

2. **Extraction Quality**
   - Title specificity
   - Body content length
   - Number of images

3. **Timing**
   - Total extraction time
   - Time per stage
   - Identify bottlenecks

4. **Success Rate**
   - Percentage of successful extractions
   - Common failure patterns
   - Sites that need special handling

## Conclusion

Dynamic content loading is a fundamental challenge in modern web scraping. Our multi-stage waiting strategy provides a reliable, generic solution that works for most websites without requiring site-specific code.

The key insight: **Wait long enough for JavaScript to execute and content to load, but not so long that it impacts performance.**

Current defaults (5s + 3s) provide a good balance for most use cases, with easy configuration for special cases.