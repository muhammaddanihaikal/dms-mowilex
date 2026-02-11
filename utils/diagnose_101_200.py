import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from dotenv import load_dotenv

load_dotenv()

def test_full_diagnose_101_200(page):
    login_page = LoginPage(page)
    login_page.navigate()
    username = os.getenv("DMS_USERNAME")
    password = os.getenv("DMS_PASSWORD")
    login_page.login(username, password)
    
    faktur_pajak_page = FakturPajakPage(page)
    faktur_pajak_page.navigate_to_menu()
    
    # Try to set records per page
    try:
        faktur_pajak_page.set_records_per_page("100")
    except:
        pass
    
    print("\n--- FULL DIAGNOSE ROW 101-200 (No Filter) ---")
    
    # Go to page 2 (assuming 100 per page)
    if faktur_pajak_page.has_next_page():
        faktur_pajak_page.go_to_next_page()
    else:
        print("No more pages.")
        return
        
    rows = faktur_pajak_page.get_all_rows()
    
    for i, row in enumerate(rows):
        total_index = 101 + i
        fp_code = faktur_pajak_page.get_faktur_pajak_code(row)
        invoice_num = faktur_pajak_page.get_invoice_number(row)
        
        status = "OK"
        if invoice_num == "-":
            status = "EMPTY"
        elif len(invoice_num) < 11:
            status = f"SHORT ({len(invoice_num)} chars)"
            
        print(f"Row {total_index:3}: {fp_code} | {invoice_num:15} | {status}")
