"""
TEST: Memperbaiki nomor invoice yang bermasalah (panjang < 11 karakter atau awalan 'IN20').
Alur: Download PDF -> Ekstrak Invoice Benar -> Update di Aplikasi DMS.
"""
import os
import pytest
from pages.login_page import LoginPage
from pages.faktur_pajak_page import FakturPajakPage
from dotenv import load_dotenv

load_dotenv()

def test_faktur_pajak_fix_short_invoice(page):
    """
    Test to check Faktur Pajak records with 'Not Match' status,
    specifically those with Invoice Number length < 11.
    It will download the PDF, extract the correct invoice number,
    and update the record in the app.
    """
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
    # print("Applying 'Not Match' filter...")
    # faktur_pajak_page.apply_filter_not_match()
    
    # 4. Optional Date Filter (Comment out if not needed)
    # faktur_pajak_page.apply_date_filter("2026-02-10", "2026-02-10")
    
    # Set to 100 records per page
    faktur_pajak_page.set_records_per_page("100")
    
    total_records = faktur_pajak_page.get_total_records()
    print(f"Total 'Not Match' records found: {total_records}")

    if total_records == 0:
        print("No records to process.")
        return

    total_seen = 0
    current_page = 1

    # --- CONFIGURATION ---
    SPECIFIC_FP = None # Set to None to process range
    START_RECORD = 501
    END_RECORD = 1000 # Final re-check from 501 to 1000
    # ---------------------
    
    if SPECIFIC_FP:
        print(f"Searching for specific FP: {SPECIFIC_FP}")
        faktur_pajak_page.search(SPECIFIC_FP)
        END_RECORD = 1
    else:
        # Skipping pages to reach START_RECORD
        target_page = ((START_RECORD - 1) // 100) + 1
        while current_page < target_page:
            if faktur_pajak_page.has_next_page():
                print(f"Skipping page {current_page}...")
                faktur_pajak_page.go_to_next_page()
                current_page += 1
                total_seen += 100
            else:
                break

    print(f"Starting fix process for records {START_RECORD} to {END_RECORD}...")
    
    records_fixed = 0
    
    while total_seen < END_RECORD:
        rows = faktur_pajak_page.get_all_rows()
        if not rows:
            break
            
        print(f"\n--- Processing Page {current_page} ({len(rows)} rows) ---")
        
        for i in range(len(rows)):
            total_seen += 1
            if total_seen < START_RECORD:
                continue
            if total_seen > END_RECORD:
                break
                
            try:
                # Re-locate row for stability
                current_rows = faktur_pajak_page.get_all_rows()
                if i >= len(current_rows):
                    break
                
                current_row = current_rows[i]
                
                fp_code = faktur_pajak_page.get_faktur_pajak_code(current_row)
                invoice_num = faktur_pajak_page.get_invoice_number(current_row)
                
                # Check for short or missing invoice
                is_short = (len(invoice_num) < 11 and invoice_num != "-")
                is_missing = (invoice_num == "-")
                is_wrong_prefix = invoice_num.upper().startswith("IN20")
                
                if is_short or is_missing or is_wrong_prefix:
                    print(f"[{total_seen}/{END_RECORD}] {fp_code} | {invoice_num} -> ", end="", flush=True)
                    
                    pdf_path = faktur_pajak_page.download_pdf(current_row)
                    if pdf_path:
                        extracted_inv = faktur_pajak_page.extract_invoice_from_pdf(pdf_path)
                        if extracted_inv and len(extracted_inv) >= 11:
                            faktur_pajak_page.update_invoice_number(current_row, extracted_inv)
                            print(f"{extracted_inv} (OK)")
                            records_fixed += 1
                        else:
                            print(f"Skipped (PDF Data Issue)")
                    else:
                        print("Skipped (Download Error)")
                else:
                    # Print OK on the same line for non-problematic rows to keep output clean
                    print(f"[{total_seen}/{END_RECORD}] {fp_code} | OK", end="\r", flush=True)
                    
            except Exception as e:
                print(f"\n[{total_seen}] Error: {str(e)}")
                continue
        
        if total_seen < END_RECORD and faktur_pajak_page.has_next_page():
            print("\nMoving to next page...")
            faktur_pajak_page.go_to_next_page()
            current_page += 1
        else:
            break
            
    print(f"\n========================================")
    print(f"Process completed.")
    print(f"Total processed: {total_seen}")
    print(f"Total fixed: {records_fixed}")
    print(f"========================================")
