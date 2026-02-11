import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from dotenv import load_dotenv

load_dotenv()

def test_list_invoice_lengths(page):
    login_page = LoginPage(page)
    login_page.navigate()
    username = os.getenv("DMS_USERNAME")
    password = os.getenv("DMS_PASSWORD")
    login_page.login(username, password)
    
    faktur_pajak_page = FakturPajakPage(page)
    faktur_pajak_page.navigate_to_menu()
    
    # Set to 100 records per page
    faktur_pajak_page.set_records_per_page("100")
    
    print("\n--- Listing first 100 rows (No Filter) ---")
    rows = faktur_pajak_page.get_all_rows()
    
    short_rows = []
    
    for i, row in enumerate(rows):
        fp_code = faktur_pajak_page.get_faktur_pajak_code(row)
        invoice_num = faktur_pajak_page.get_invoice_number(row)
        
        if invoice_num != "-" and len(invoice_num) < 11:
            short_rows.append((i + 1, fp_code, invoice_num))
            print(f"Row {i+1}: {fp_code} | '{invoice_num}' | Length: {len(invoice_num)} (SHORT)")
        else:
            # Verbose for debugging why they might be skipped
            # print(f"Row {i+1}: {fp_code} | '{invoice_num}' | Length: {len(invoice_num)}")
            pass

    print(f"\nTotal short invoices found in first 100 rows: {len(short_rows)}")
    if short_rows:
        print("Problematic rows indices:", [r[0] for r in short_rows])
