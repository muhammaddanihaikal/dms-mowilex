import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from dotenv import load_dotenv

load_dotenv()

def test_full_diagnose_100(page):
    login_page = LoginPage(page)
    login_page.navigate()
    username = os.getenv("DMS_USERNAME")
    password = os.getenv("DMS_PASSWORD")
    login_page.login(username, password)
    
    faktur_pajak_page = FakturPajakPage(page)
    faktur_pajak_page.navigate_to_menu()
    
    # Set to 100 records per page
    faktur_pajak_page.set_records_per_page("100")
    
    print("\n--- FULL DIAGNOSE ROW 1-100 (No Filter) ---")
    rows = faktur_pajak_page.get_all_rows()
    
    for i, row in enumerate(rows):
        fp_code = faktur_pajak_page.get_faktur_pajak_code(row)
        invoice_num = faktur_pajak_page.get_invoice_number(row)
        
        status = "OK"
        if invoice_num == "-":
            status = "EMPTY"
        elif len(invoice_num) < 11:
            status = f"SHORT ({len(invoice_num)} chars)"
            
        print(f"Row {i+1:3}: {fp_code} | {invoice_num:15} | {status}")
