# URL Content Extractor

Extract clean, readable content from any webpage URL — built for **AI agents** to consume programmatically.

**Paid per-use** via [Nevermined](https://nevermined.ai) x402 protocol. $1 for 100 extracts (1¢ each). Pre-paid credits never expire.

## How It Works

```
POST /extract
Authorization: Bearer <your-api-key>
Content-Type: application/json

{ "url": "https://example.com/article" }
```

Response:
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Clean extracted text without ads, nav, or scripts...",
  "credits_remaining": 95
}
```

## For AI Agents

This API is designed to be called by other AI agents:
- **x402 payments** — agent pays per-request automatically
- **Clean output** — no HTML, no ads, just the content
- **Fast** — sub-second extraction for most pages
- **Credit-based** — 100 credits per purchase, 1 credit per extract

### MCP Integration

Claude, Cursor, and other MCP-compatible agents can discover and use this service as an MCP tool.

## For Humans

1. Purchase credits at [nevermined.app](https://nevermined.app)
2. Get your API key
3. Call `POST /extract` with your URL

## Tech Stack

- **FastAPI** — async Python web framework
- **BeautifulSoup** — content extraction
- **Nevermined payments-py** — x402 payment verification
- **httpx** — async HTTP client

## Deployment

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

## License

MIT
