from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

def dump_actions_html():
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
        
        # Navigate
        page.goto(os.getenv("BASE_URL") + "admin/attachment-faktur-pajaks")
        
        # Search for row 25 code: 04002600030250979
        search_input = page.locator("input[type='search']").first
        search_input.fill("04002600030250979")
        page.wait_for_timeout(3000)
        
        # Get row
        row = page.locator("table.fi-ta-table tbody tr").first
        if row.count() > 0:
            # Get last cell (Actions)
            actions_cell = row.locator("td").last
            html = actions_cell.inner_html()
            print("--- ACTIONS CELL HTML ---")
            print(html)
            print("--- END HTML ---")
            
            # Screenshot
            page.screenshot(path="actions_cell.png")
        else:
            print("Row not found")

        browser.close()

if __name__ == "__main__":
    dump_actions_html()
