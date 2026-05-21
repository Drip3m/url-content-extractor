"""
URL Content Extractor API — Paid per-use via Nevermined
"""
import os
import base64
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import re

from payments_py import Payments, PaymentOptions
from payments_py.x402.helpers import build_payment_required

# ── Config ──────────────────────────────────────────────
NVM_API_KEY = os.getenv("NVM_API_KEY")
AGENT_ID = os.getenv("NVM_AGENT_ID")
PLAN_ID = os.getenv("NVM_PLAN_ID")
ENVIRONMENT = os.getenv("NVM_ENV", "live")
PORT = int(os.getenv("PORT", "8080"))

# ── Init Nevermined ─────────────────────────────────────
payments = Payments.get_instance(
    PaymentOptions(
        nvm_api_key=NVM_API_KEY,
        environment=ENVIRONMENT,
    )
)

# ── FastAPI ─────────────────────────────────────────────
app = FastAPI(title="URL Content Extractor", version="1.0.0")


class ExtractRequest(BaseModel):
    url: str


class ExtractResponse(BaseModel):
    url: str
    title: str
    content: str
    credits_remaining: int | None = None


# ── Payment Middleware ──────────────────────────────────
async def verify_payment(request: Request):
    """Verify the x402 payment token before processing."""
    if not AGENT_ID or not PLAN_ID:
        # Running without payment config — allow for testing
        return None

    payment_required = build_payment_required(
        plan_id=PLAN_ID,
        endpoint=str(request.url),
        agent_id=AGENT_ID,
        http_verb=request.method,
    )

    x402_token = request.headers.get("payment-signature")

    if not x402_token:
        # Return 402 with payment-required header
        pr_base64 = base64.b64encode(
            payment_required.model_dump_json(by_alias=True).encode()
        ).decode()
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Payment Required",
                "message": "Purchase a plan to access this API",
            },
            headers={"payment-required": pr_base64},
        )

    # Verify permissions
    verification = payments.facilitator.verify_permissions(
        payment_required=payment_required,
        x402_access_token=x402_token,
        max_amount="1",
    )

    if not verification["is_valid"]:
        raise HTTPException(
            status_code=402,
            detail={"error": verification.get("invalid_reason", "Invalid payment")},
        )

    return payment_required, x402_token


# ── Content Extraction ──────────────────────────────────
def extract_content(url: str) -> tuple[str, str]:
    """Fetch a URL and extract clean text content."""
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        resp = client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ContentExtractor/1.0)"
        })
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Get text and clean it up
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = [line for line in lines if line]
    content = "\n".join(clean_lines)

    # Truncate if too long
    if len(content) > 100_000:
        content = content[:100_000] + "\n\n[...content truncated at 100K chars]"

    return title, content


# ── Routes ──────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract(request: Request, body: ExtractRequest):
    # Verify payment first
    payment_info = await verify_payment(request)

    try:
        title, content = extract_content(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract: {str(e)}")

    # Settle the payment (burn 1 credit)
    credits_remaining = None
    if payment_info:
        payment_required, x402_token = payment_info
        settlement = payments.facilitator.settle_permissions(
            payment_required=payment_required,
            x402_access_token=x402_token,
            max_amount="1",
        )
        if "credits_remaining" in settlement:
            credits_remaining = settlement["credits_remaining"]

    return ExtractResponse(
        url=body.url,
        title=title,
        content=content,
        credits_remaining=credits_remaining,
    )


# ── Main ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
