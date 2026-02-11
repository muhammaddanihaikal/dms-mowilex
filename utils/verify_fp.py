import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from dotenv import load_dotenv

load_dotenv()

def test_verify_fp_status(page):
    login_page = LoginPage(page)
    login_page.navigate()
    username = os.getenv("DMS_USERNAME")
    password = os.getenv("DMS_PASSWORD")
    login_page.login(username, password)
    
    faktur_pajak_page = FakturPajakPage(page)
    faktur_pajak_page.navigate_to_menu()
    
    # Do NOT apply "Not Match" filter so we can see it if it's now Match
    fp_code = "07002600036269995"
    print(f"Searching for {fp_code}...")
    faktur_pajak_page.search(fp_code)
    
    rows = faktur_pajak_page.get_all_rows()
    if rows:
        target_row = rows[0]
        code = faktur_pajak_page.get_faktur_pajak_code(target_row)
        inv = faktur_pajak_page.get_invoice_number(target_row)
        status = faktur_pajak_page.get_status_invoice(target_row)
        print(f"RESULT: Code={code}, Invoice={inv}, Status={status}")
    else:
        print("Not found in current view.")
