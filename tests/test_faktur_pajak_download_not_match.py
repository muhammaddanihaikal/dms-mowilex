"""
TEST: Mengecek apakah PDF Faktur Pajak bisa didownload atau 'Not Found'.
Hasilnya dicatat ke dalam file log txt (misal: not_found_faktur_pajak.txt).
"""
import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from utils.file_utils import append_to_not_found_file, write_header_to_not_found_file
from dotenv import load_dotenv

load_dotenv()

def test_faktur_pajak_download_not_match(page):
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
    
    # 4. Filter Date: 10 Feb 2026 to 10 Feb 2026
    faktur_pajak_page.apply_date_filter("2026-02-10", "2026-02-10")
    
    # Set to 100 records per page
    faktur_pajak_page.set_records_per_page("100")
    
    # 4. Iterate Rows and Download
    total_seen = 0
    start_at = 1
    end_at = faktur_pajak_page.get_total_records()
    print(f"Total records found: {end_at}")
    
    if end_at == 0:
        print("No records found for the given filter.")
        return
    
    last_date_logged = None
    
    # Skip pages to get to the start_at range
    # Since 100 per page, row 201 is on Page 3
    current_page = 1
    target_page = ((start_at - 1) // 100) + 1
    
    while current_page < target_page:
        if faktur_pajak_page.has_next_page():
            print(f"Skipping page {current_page}...")
            faktur_pajak_page.go_to_next_page()
            current_page += 1
            total_seen += 100
        else:
            break

    while total_seen < end_at:
        rows = faktur_pajak_page.get_all_rows()
        if not rows:
            break
            
        print(f"Processing page {current_page}... Found {len(rows)} rows.")
        
        for i, row in enumerate(rows):
            total_seen += 1
            
            # Skip rows before start_at
            if total_seen < start_at:
                continue
            # Stop if reached end_at
            if total_seen > end_at:
                break
                
            # Re-locate row for stability
            current_rows = faktur_pajak_page.get_all_rows()
            if i >= len(current_rows):
                break
            
            current_row = current_rows[i]
            code = faktur_pajak_page.get_faktur_pajak_code(current_row)
            upload_date = faktur_pajak_page.get_upload_date(current_row)
            
            print(f"[{total_seen}/{end_at}] Processing: {code} ({upload_date})...", end=" ", flush=True)
            
            result = faktur_pajak_page.download_and_check(current_row)
            print(result)
            
            if result == "Not Found":
                if upload_date != last_date_logged:
                    write_header_to_not_found_file(upload_date)
                    last_date_logged = upload_date
                append_to_not_found_file(code, upload_date)
        
        if total_seen < end_at and faktur_pajak_page.has_next_page():
            print("Moving to next page...")
            faktur_pajak_page.go_to_next_page()
            current_page += 1
        else:
            break
            
    print(f"Process completed. Total seen: {total_seen}")
