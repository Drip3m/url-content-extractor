import gradio as gr
import httpx
import os

API_URL = os.getenv("API_URL", "https://url-content-extractor-n56a.onrender.com")

def extract_url(url):
    """Call the extraction API (will require payment in production)."""
    if not url or not url.startswith(("http://", "https://")):
        return "Please enter a valid URL starting with http:// or https://", ""
    
    try:
        resp = httpx.post(
            f"{API_URL}/extract",
            json={"url": url},
            timeout=30.0,
        )
        
        if resp.status_code == 402:
            data = resp.json()
            msg = data.get("detail", {}).get("message", "Payment required")
            return (
                f"## ❌ Payment Required\n\n{msg}\n\n"
                f"Purchase credits at [nevermined.app](https://nevermined.app) "
                f"to use this service. $1 for 100 extracts (1¢ each).",
                "https://nevermined.app"
            )
        
        if resp.status_code == 200:
            data = resp.json()
            content = f"# {data['title']}\n\n{data['content']}"
            credits = data.get("credits_remaining", "?")
            return content, f"**Credits remaining: {credits}**"
        
        return f"## ⚠️ Error\n\nStatus {resp.status_code}: {resp.text}", ""
    
    except httpx.TimeoutException:
        return (
            "## ⏳ Request Timeout\n\nThe free tier service is waking up "
            "(can take ~30s). Please try again.",
            ""
        )
    except Exception as e:
        return f"## ⚠️ Error\n\n{str(e)}", ""


with gr.Blocks(
    title="URL Content Extractor",
    theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
) as demo:
    gr.Markdown(
        """
        # 🌐 URL Content Extractor
        
        **Extract clean, readable content from any webpage** — no ads, no nav, no scripts.
        
        Built for AI agents. Powered by [Nevermined](https://nevermined.app) x402 payments.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            url_input = gr.Textbox(
                label="Enter URL",
                placeholder="https://example.com/article",
                lines=1,
            )
            extract_btn = gr.Button("Extract", variant="primary")
        
        with gr.Column(scale=1):
            gr.Markdown(
                """
                ### 💰 Pricing
                - **$1** for **100 extracts**
                - 1¢ per extraction
                - Credits never expire
                
                ### 🔗 Links
                - [Purchase Credits](https://nevermined.app)
                - [GitHub](https://github.com/Drip3m/url-content-extractor)
                - [API Docs](https://github.com/Drip3m/url-content-extractor#readme)
                """
            )
    
    status = gr.Markdown("Ready")
    output = gr.Markdown("", label="Extracted Content")
    
    extract_btn.click(
        fn=extract_url,
        inputs=url_input,
        outputs=[output, status],
    )


if __name__ == "__main__":
    demo.launch()
