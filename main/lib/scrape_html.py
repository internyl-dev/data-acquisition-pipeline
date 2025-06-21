
from playwright.async_api import async_playwright

async def get_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    return html