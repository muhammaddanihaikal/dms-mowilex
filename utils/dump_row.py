from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

def dump_row_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Login
        page.goto(os.getenv("BASE_URL") + "admin/login")
        page.fill("input[type='email']", os.getenv("DMS_USERNAME"))
        page.fill("input[type='password']", os.getenv("DMS_PASSWORD"))
        page.click("button[type='submit']")
        page.wait_for_url("**/admin")
        
        # Navigate to Faktur Pajak
        page.goto(os.getenv("BASE_URL") + "admin/attachment-faktur-pajaks")
        page.wait_for_selector("table.fi-ta-table tbody tr")
        
        # Get first row HTML
        first_row = page.locator("table.fi-ta-table tbody tr").first
        html_content = first_row.inner_html()
        
        print("--- START ROW HTML ---")
        print(html_content)
        print("--- END ROW HTML ---")

        # Take screenshot
        page.screenshot(path="faktur_pajak_row.png")
        
        browser.close()

if __name__ == "__main__":
    dump_row_html()
