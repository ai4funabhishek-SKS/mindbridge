# DeepSeek LLM Conversation Extractor

This script uses Playwright and python-docx to extract all conversations from the DeepSeek LLM web page and save them to a Word file with timestamps.

## Instructions
1. Install dependencies:
   ```
   pip install playwright python-docx
   playwright install
   ```
2. Update the CSS selectors in the script to match the DeepSeek LLM chat page structure.
3. Run the script. The output will be saved as `raw_data_deepseek.docx`.

## Python Script
```python
import asyncio
from playwright.async_api import async_playwright
from docx import Document

async def main():
    url = "https://deepseek.com/llm"  # Replace with the actual DeepSeek LLM chat URL
    document = Document()
    document.add_heading('DeepSeek LLM Conversations', 0)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        # Adjust these selectors based on the actual page structure
        messages = await page.query_selector_all('.message-selector')  # Replace with actual selector
        for msg in messages:
            text = await msg.inner_text()
            timestamp = await msg.query_selector('.timestamp-selector')  # Replace with actual selector
            time_text = await timestamp.inner_text() if timestamp else "No timestamp"
            document.add_paragraph(f"{time_text}: {text}")

        document.save("raw_data_deepseek.docx")
        await browser.close()

asyncio.run(main())
```

---

Let me know if you need help with the selectors or want to automate running this script.
