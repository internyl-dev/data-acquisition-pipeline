import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
        html = await page.content()
        await browser.close()
    return html

print(asyncio.run(main()))