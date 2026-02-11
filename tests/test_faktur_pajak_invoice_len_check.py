"""
TEST: Mencari dan mendata (logging) Faktur Pajak yang nomor invoice-nya kurang dari 11 karakter.
Hanya melakukan pengecekan (Read-only), tidak melakukan update.
"""
import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from utils.file_utils import append_to_not_found_file
from dotenv import load_dotenv

load_dotenv()

def test_faktur_pajak_invoice_length_check(page):
    # 1. Login
    login_page = LoginPage(page)
    login_page.navigate()
    
    username = os.getenv("DMS_USERNAME")
    password = os.getenv("DMS_PASSWORD")
    
    if not username or not password:
        pytest.fail("Credentials not found in .env file")
        
    login_page.login(username, password)
    
    # 2. Navigate to Faktur Pajak
    faktur_pajak_page = FakturPajakPage(page)
    faktur_pajak_page.navigate_to_menu()
    
    # 3. Filter Status Invoice = "Not Match"
    faktur_pajak_page.apply_filter_not_match()
    
    # Set to 100 records per page
    faktur_pajak_page.set_records_per_page("100")
    
    # 4. Iterate Rows and Check Length
    total_seen = 0
    start_at = 2000
    limit = 2981
    log_filename = "short_invoice_faktur_pajak.txt"
    current_page = 1
    
    # Skipping pages to reach start_at
    target_page = ((start_at - 1) // 100) + 1
    while current_page < target_page:
        if faktur_pajak_page.has_next_page():
            print(f"Skipping page {current_page}...")
            faktur_pajak_page.go_to_next_page()
            current_page += 1
            total_seen += 100
        else:
            break

    print(f"Checking Invoice Numbers ({start_at}-{limit}) for length < 11...")
    
    while total_seen < limit:
        rows = faktur_pajak_page.get_all_rows()
        if not rows:
            break
            
        print(f"Processing page {current_page}... Found {len(rows)} rows.")
        
        for i in range(len(rows)):
            total_seen += 1
            # Skip rows before start_at
            if total_seen < start_at:
                continue
            # Stop if reached limit
            if total_seen > limit:
                break
                
            try:
                # Re-locate everything to be safe
                current_rows = faktur_pajak_page.get_all_rows()
                if i >= len(current_rows):
                    break
                
                current_row = current_rows[i]
                
                # Get text with a shorter timeout for individual cells
                fp_code = current_row.locator("td").nth(1).inner_text(timeout=5000).strip()
                invoice_num = current_row.locator("td").nth(2).inner_text(timeout=5000).strip()
                
                # Show progress
                print(f"[{total_seen}/{limit}] Checking: {invoice_num}...", end="\r", flush=True)
                
                # Check length of invoice number
                if len(invoice_num) < 11 and invoice_num != "-" and invoice_num != "":
                    print(f"\n[{total_seen}/{limit}] Found Short Invoice: {invoice_num} (Code: {fp_code}) -> Logging to {log_filename}")
                    append_to_not_found_file(fp_code, filename=log_filename)
            except Exception as e:
                print(f"\n[Error] Skipping row {i+1} on this page due to error: {str(e)}")
                continue
        
        if total_seen < limit and faktur_pajak_page.has_next_page():
            print("\nMoving to next page...")
            faktur_pajak_page.go_to_next_page()
            current_page += 1
        else:
            break
            
    print(f"\nProcess completed. Total seen: {total_seen}")
