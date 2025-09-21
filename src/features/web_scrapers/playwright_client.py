
from playwright.async_api import async_playwright
from typing import Optional

class PlaywrightClient:
    """
    The Playwright client to scrape the contents from a webpage given a URL
    """
    def __init__(self, headless=True):
        self.headless = headless

    async def scrape_url(self, url) -> str:
        """
        Sends URL to Playwright to extract HTML contents

        Args:
            url (str): URL to target website
        
        Returns:
            raw_html (str): The contents of the HTML of the target website
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36")
            page = await context.new_page()
            await page.goto(url)
            raw_html = await page.evaluate('document.body.innerHTML')

            # Other procedures
            favicon = self.scrape_favicon()

            await browser.close()
        
        return raw_html, favicon
    
    async def scrape_favicon(self, page) -> Optional[str]:
        """
        Extract favicon from the current page
        
        Args:
            page: Playwright page object
            
        Returns:
            Optional[str]: Favicon URL or base64 data, None if not found
        """
        try:
            # Method 1: Look for favicon link tags
            favicon_selectors = [
                'link[rel="icon"]',
                'link[rel="shortcut icon"]', 
                'link[rel="apple-touch-icon"]',
                'link[rel="apple-touch-icon-precomposed"]'
            ]
            
            for selector in favicon_selectors:
                element = await page.query_selector(selector)
                if element:
                    href = await element.get_attribute('href')
                    if href:
                        # Convert relative URLs to absolute
                        if href.startswith('//'):
                            return f"https:{href}"
                        elif href.startswith('/'):
                            base_url = await page.evaluate('window.location.origin')
                            return f"{base_url}{href}"
                        elif not href.startswith('http'):
                            current_url = await page.evaluate('window.location.href')
                            base_url = '/'.join(current_url.split('/')[:-1])
                            return f"{base_url}/{href}"
                        return href
            
            # Method 2: Try default favicon.ico location
            base_url = await page.evaluate('window.location.origin')
            default_favicon = f"{base_url}/favicon.ico"
            
            # You could optionally verify if this URL exists
            return default_favicon
            
        except Exception as e:
            print(f"Error scraping favicon: {e}")
            return None