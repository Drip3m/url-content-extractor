---
name: url-content-extractor
description: "Extract clean, readable text from any webpage URL. Removes ads, navigation, scripts, and clutter — returns just the article content. Supports paid credit-based usage via Nevermined x402."
version: 1.0.0
author: Drip3m
tags: [web-scraping, content-extraction, url-to-text, research]
---

# URL Content Extractor

Extract clean, readable text content from any webpage URL. Designed for AI agents that need to consume web content programmatically.

## How to Use

When a user asks you to extract content from a URL, use the `url-content-extractor` MCP server if configured, or call the API directly.

### Direct API Call

```python
POST https://url-content-extractor-n56a.onrender.com/extract
Content-Type: application/json

{ "url": "https://example.com/article" }
```

### Payment

The service uses **Nevermined x402** for agent-to-agent payments:
- Plans purchased at nevermined.app
- $1 for 100 credits (1¢ per extraction)
- Pre-paid credits never expire
- Include `payment-signature` header with valid x402 token

### Response Format

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Clean extracted text without ads, nav, or scripts...",
  "credits_remaining": 95
}
```

### Error Handling

- `402 Payment Required` → No valid payment token. Purchase a plan at nevermined.app
- `400 Bad Request` → Invalid URL or fetch failure
- Content truncated at 100K characters

### What Gets Removed

The extractor automatically removes:
- Script tags, style tags, navigation, footers, headers, aside elements
- Empty lines and excessive whitespace
- Only meaningful article/conent text is preserved

## When to Trigger

Ask the user if you should extract content when they:
- Share a news article URL
- Reference a blog post or documentation page
- Need to analyze web page content
- Want to summarize or rephrase content from a URL

## Limitations

- Maximum 100K character output
- 30-second fetch timeout
- Requires purchased credits on Nevermined
- May not work well with JavaScript-rendered content (SPAs)
- Free tier Render service may have ~30s cold start
