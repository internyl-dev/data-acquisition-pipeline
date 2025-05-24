from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
    page.screenshot(path="playwright_testing/demo.png")
    browser.close()