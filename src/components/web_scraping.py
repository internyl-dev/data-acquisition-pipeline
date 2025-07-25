
from playwright.async_api import async_playwright

class WebScraping:
    def __init__(self, headless):
        self.headless = headless

    async def scrape_html(self, url):
        """
        Sends URL to Playwright to extract HTML contents.

        Args:
            url (str): URL to target website
        
        Returns:
            html_contents (str): The contents of the HTML of the target website
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36")
            page = await context.new_page()
            await page.goto(url)
            html = await page.evaluate('document.body.innerHTML')
            await browser.close()
        
        return html