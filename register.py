"""
Register the URL Content Extractor agent + payment plan on Nevermined.

Usage:
    python register.py  (uses .env for config)
"""
import os
from dotenv import load_dotenv
load_dotenv()

from payments_py import Payments, PaymentOptions
from payments_py.plans import get_erc20_price_config, get_fixed_credits_config

# USDC on Base (mainnet)
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

def main():
    nvm_api_key = os.getenv("NVM_API_KEY")
    builder_address = os.getenv("BUILDER_ADDRESS")
    environment = os.getenv("NVM_ENV", "live")

    if not builder_address:
        print("❌ Please set BUILDER_ADDRESS in .env (your wallet address)")
        return

    payments = Payments.get_instance(
        PaymentOptions(
            nvm_api_key=nvm_api_key,
            environment=environment,
        )
    )

    print("📡 Registering agent with Nevermined...")

    result = payments.agents.register_agent_and_plan(
        agent_metadata={
            "name": "URL Content Extractor",
            "description": "Extract clean, readable content from any URL. Perfect for AI agents that need to read web pages.",
            "tags": ["web-scraping", "content-extraction", "url-to-markdown", "ai-agent"],
        },
        agent_api={
            "endpoints": [
                {"verb": "POST", "url": "https://url-extractor.onrender.com/extract"}
            ]
        },
        plan_metadata={
            "name": "Pay-Per-Extract",
            "description": "1 credit = 1 URL extraction. Pre-paid credits never expire.",
        },
        price_config=get_erc20_price_config(
            1_000_000,      # 1 USDC for 100 credits = $0.01 per extraction
            USDC_ADDRESS,
            builder_address,
        ),
        credits_config=get_fixed_credits_config(100, 1),  # 100 credits, 1 per use
        access_limit="credits",
    )

    print(f"\n✅ Registered!")
    print(f"   Agent ID: {result['agentId']}")
    print(f"   Plan ID:  {result['planId']}")
    print("\n📝 Add these to your .env file:")
    print(f'   NVM_AGENT_ID={result["agentId"]}')
    print(f'   NVM_PLAN_ID={result["planId"]}')
