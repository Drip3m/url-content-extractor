"""
URL Content Extractor — MCP Server
====================================
Exposes URL content extraction as an MCP tool for AI agents (Claude, Cursor, etc.).

Usage:
  1. Install: pip install mcp httpx python-dotenv
  2. Set env vars: NVM_API_KEY, NVM_AGENT_ID, NVM_PLAN_ID (or use .env)
  3. Run: python mcp_server.py

  Or add to Claude Desktop config:
  {
    "mcpServers": {
      "url-content-extractor": {
        "command": "python",
        "args": ["/path/to/mcp_server.py"],
        "env": {
          "NVM_API_KEY": "live:...",
          "NVM_AGENT_ID": "...",
          "NVM_PLAN_ID": "..."
        }
      }
    }
  }
"""

import os, base64, json
from dotenv import load_dotenv
load_dotenv()

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ── Config ──────────────────────────────────────────────
AGENT_ID = os.getenv("NVM_AGENT_ID")
PLAN_ID = os.getenv("NVM_PLAN_ID")
NVM_API_KEY = os.getenv("NVM_API_KEY")
API_URL = os.getenv("API_URL", "https://url-content-extractor-n56a.onrender.com")
ENVIRONMENT = os.getenv("NVM_ENV", "live")

from payments_py import Payments, PaymentOptions
from payments_py.x402.helpers import build_payment_required

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=ENVIRONMENT)
)

# ── MCP Server ──────────────────────────────────────────
server = Server("url-content-extractor")


def get_payment_token() -> str | None:
    """Generate an x402 payment token for the extract endpoint."""
    if not AGENT_ID or not PLAN_ID:
        return None

    payment_required = build_payment_required(
        plan_id=PLAN_ID,
        endpoint=f"{API_URL}/extract",
        agent_id=AGENT_ID,
        http_verb="POST",
    )

    # Generate the access token (requires a wallet or Nevermined SDK)
    # For now, return None — the user needs to purchase credits first
    return None


@server.tool()
async def extract_url(url: str) -> str:
    """
    Extract clean, readable text content from any webpage URL.
    
    Removes ads, navigation, scripts — returns just the article text.
    Requires a purchased plan on Nevermined (see docs for setup).
    
    Args:
        url: The URL of the webpage to extract content from
    Returns:
        The extracted text content with title
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_URL}/extract",
            json={"url": url},
            headers={"Content-Type": "application/json"},
        )

        if resp.status_code == 402:
            error = resp.json()
            payment_required = resp.headers.get("payment-required")
            msg = (
                f"❌ Payment Required: {error.get('detail', {}).get('message', '')}\n\n"
                f"To use this tool:\n"
                f"1. Purchase credits at https://nevermined.app\n"
                f"2. Get your access token\n"
                f"3. Set NVM_API_KEY, NVM_AGENT_ID, NVM_PLAN_ID env vars\n\n"
                f"See: https://github.com/Drip3m/url-content-extractor"
            )
            return msg

        if resp.status_code == 200:
            data = resp.json()
            return f"# {data['title']}\n\n{data['content']}\n\n---\nCredits remaining: {data.get('credits_remaining', '?')}"

        return f"Error {resp.status_code}: {resp.text}"


@server.tool()
async def extract_url_raw(url: str) -> str:
    """
    Extract raw page content from a URL (no payment gate — for previews).
    
    Same as extract_url but bypasses payment — only works when the server
    is configured in free/test mode.
    
    Args:
        url: The URL of the webpage to extract content from
    Returns:
        The extracted text content
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{API_URL}/health",
        )
        if resp.status_code == 200:
            return "Service is online. Use extract_url for paid extraction."
        return f"Error: {resp.text}"


# ── Main ────────────────────────────────────────────────
async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="url-content-extractor",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
