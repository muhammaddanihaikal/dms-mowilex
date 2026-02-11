from playwright.sync_api import Page, expect
import os

class FakturPajakPage:
    def __init__(self, page: Page):
        self.page = page
        self.menu_attachment_documents = page.get_by_role("button", name="Attachment Documents")
        self.menu_faktur_pajak = page.get_by_role("link", name="Faktur Pajak")
        
        # Filter elements
        self.filter_button = page.get_by_role("button", name="Filter")
        self.status_invoice_select = page.locator("#tableFilters\\.invoice_status\\.value")
        self.from_date_input = page.get_by_label("From Date")
        self.to_date_input = page.get_by_label("To Date")
        self.total_records_text = page.locator("span.fi-pagination-overview")


        
        # Table elements
        self.table_rows = page.locator("table.fi-ta-table tr").filter(has_text="Not Match")
        self.records_per_page_select = page.locator("select:visible").filter(has=page.locator("option[value='100']")).first

    def set_records_per_page(self, count="100"):
        self.records_per_page_select.wait_for(state="visible", timeout=5000)
        self.records_per_page_select.select_option(count)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000) # Give it more time to re-render

    def navigate_to_menu(self):
        # Check if already on the page
        if "/admin/attachment-faktur-pajaks" not in self.page.url:
            # Sometimes we need to expand the menu first
            if self.menu_attachment_documents.is_visible():
                is_expanded = self.menu_attachment_documents.get_attribute("aria-expanded") == "true"
                if not is_expanded:
                    self.menu_attachment_documents.click()
            self.menu_faktur_pajak.click()
            self.page.wait_for_load_state("networkidle")

    def apply_filter_not_match(self):
        # Open filter if not already
        # The filter panel might be hidden
        if not self.status_invoice_select.is_visible():
            self.filter_button.click()
        
        self.status_invoice_select.select_option("Not Match")
        # Wait for the table to reload
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def apply_date_filter(self, from_date: str, to_date: str):
        # Open filter if not already
        if not self.from_date_input.is_visible():
            self.filter_button.click()
        
        self.from_date_input.fill(from_date)
        self.from_date_input.press("Enter")
        self.to_date_input.fill(to_date)
        self.to_date_input.press("Enter")
        
        # Wait for the table to reload
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    def get_all_rows(self):
        # We need to find the rows in the table body
        return self.page.locator("table.fi-ta-table tbody tr").all()

    def get_faktur_pajak_code(self, row):
        # Column 0 is 'No', Column 1 is 'Faktur Pajak Code'
        return row.locator("td").nth(1).inner_text().strip()

    def get_invoice_number(self, row):
        # Column 2 is 'Invoice Number'
        # Actually in the screenshot it looks like Invoice Number might be index 2 or 3
        return row.locator("td").nth(2).inner_text().strip()

    def get_upload_date(self, row):
        # Based on user feedback, index 7 is 'Jakarta', so the date is at index 8
        text = row.locator("td").nth(8).inner_text().strip()
        # text is likely "2026-02-09 10:51:14"
        # Extract only the date part
        if " " in text:
            return text.split(" ")[0]
        return text

    def download_and_check(self, row):
        download_link = row.get_by_role("link", name="Download")
        if not download_link.is_visible():
            return "Skipped (No Download Link)"
        
        # Ambil URL download dari atribut href
        url = download_link.get_attribute("href")
        if not url:
            return "Skipped (No URL)"

        try:
            # Lakukan request ke URL tersebut secara background
            response = self.page.request.get(url)
            
            # 1. Jika status 404, sudah pasti Not Found
            if response.status == 404:
                return "Not Found"
            
            content_type = response.headers.get("content-type", "").lower()
            content_disposition = response.headers.get("content-disposition", "").lower()

            # 2. Jika ada Content-Disposition 'attachment' atau 'filename', berarti ini FILE (berhasil)
            if "attachment" in content_disposition or "filename" in content_disposition:
                return "Success"

            # 3. Jika Content-Type adalah aplikasi (pdf, octet-stream, dll), berarti ini FILE
            if "application/" in content_type:
                return "Success"

            # 4. Jika Content-Type adalah HTML, kemungkinan besar ini adalah halaman ERROR
            if "text/html" in content_type:
                html_content = response.text()
                # Kita cari tanda-tanda spesifik pesan error
                # Sesuaikan kata kunci ini dengan yang muncul di layar saat error
                error_keywords = ["not found", "404", "tidak ditemukan", "tidak tersedia"]
                if any(key in html_content.lower() for key in error_keywords):
                    return "Not Found"
            
            # Jika ragu (misalnya status 200 tapi bukan kriteria di atas), kita anggap success 
            # agar tidak salah memasukkan data yang sebenarnya ada (false positive)
            return "Success"
        except Exception:
            return "Error Checking"

    def process_all_rows(self, log_callback):
        # This will be handled in the test case for better control
        pass

    def has_next_page(self):
        next_button = self.page.get_by_role("button", name="Next")
        return next_button.is_visible() and not next_button.is_disabled()

    def get_total_records(self):
        # Text is usually like "Showing 1 to 100 of 1,234 results"
        try:
            text = self.total_records_text.inner_text().strip()
            # Split by "of" and take the part before "results"
            parts = text.split("of")
            if len(parts) > 1:
                total_str = parts[1].replace("results", "").replace(",", "").strip()
                return int(total_str)
        except Exception:
            pass
        return 0

    def search(self, keyword):
        # Filament global search input
        search_input = self.page.locator("input[type='search']").first
        if search_input.is_visible():
            search_input.fill(keyword)
            # Wait for search debounce
            self.page.wait_for_timeout(1000) 
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(500) 
            return True
        return False



    def get_status_invoice(self, row):
        # The selector for the status invoice cell
        status_cell = row.locator(".fi-table-cell-invoice-status")
        return status_cell.inner_text().strip()

    def update_invoice_number(self, row, invoice_number):
        # 1. Click the Edit button (pencil icon)
        edit_button = row.locator("button[title='Edit Invoice Number']")
        edit_button.click()
        
        # 2. Wait for the input to appear
        input_field = row.locator("input.inline-edit-input")
        input_field.wait_for(state="visible", timeout=5000)
        
        # 3. Fill the invoice number
        input_field.fill(invoice_number)
        
        # 4. Click the Save button (checkmark icon)
        save_button = row.locator("button[title='Save']")
        save_button.click()
        
        # 5. Wait for the input to disappear (indicating save complete)
        input_field.wait_for(state="hidden", timeout=10000)
        
        # 6. Wait for status to become "Match"
        # We try to wait for the status badge to update
        status_cell = row.locator(".fi-table-cell-invoice-status")
        try:
            # Wait up to 15 seconds for it to change to Match
            expect(status_cell).to_contain_text("Match", timeout=15000)
        except Exception:
            print(f"      Warning: Status did not change to Match after 15s. Current: '{status_cell.inner_text().strip()}'")
        
    def go_to_next_page(self):
        next_button = self.page.get_by_role("button", name="Next")
        next_button.click()
        self.page.wait_for_load_state("networkidle")

    def download_pdf(self, row):
        # Look for Download link in the row
        download_link = row.get_by_role("link", name="Download")
        if not download_link.is_visible():
            return None
        
        # Get URL from href attribute
        url = download_link.get_attribute("href")
        if not url:
            return None

        try:
            # Perform background request
            response = self.page.request.get(url)
            if response.status != 200:
                print(f"    Download failed with status {response.status}")
                return None
            
            # Save to a temporary file
            temp_dir = os.path.join(os.getcwd(), "temp_downloads")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Try to get filename from content-disposition
            suggested_filename = "downloaded_invoice.pdf"
            cd = response.headers.get("content-disposition", "")
            if "filename=" in cd:
                suggested_filename = cd.split("filename=")[1].strip('"')
            
            path = os.path.join(temp_dir, suggested_filename)
            
            # Write bytes to file
            with open(path, "wb") as f:
                f.write(response.body())
                
            return path
        except Exception as e:
            print(f"    Error downloading PDF in background: {e}")
            return None

    def extract_invoice_from_pdf(self, pdf_path):
        from pdfminer.high_level import extract_text
        import re
        
        try:
            text = extract_text(pdf_path)
            
            # Find all potential matches from both patterns
            all_matches = []
            # Pattern 1: (Referensi: IN...)
            all_matches.extend(re.findall(r"\(Referensi:\s*([A-Za-z0-9]+)\)", text))
            # Pattern 2: Referensi: IN...
            all_matches.extend(re.findall(r"Referensi:\s*([A-Za-z0-9]+)", text))
            
            if not all_matches:
                return None
            
            # Clean and filter matches that look like valid Mowilex invoices
            # Must be >= 11 characters and start with 'IN'
            valid_invoices = [m.strip() for m in all_matches if len(m.strip()) >= 11 and m.strip().upper().startswith("IN")]
            
            if valid_invoices:
                # Prioritize IN26 (correct year) over others if available
                correct_year_invoices = [m for m in valid_invoices if m.upper().startswith("IN26")]
                if correct_year_invoices:
                    return correct_year_invoices[0] # Take the first IN26 found
                
                # If no IN26, just take the first valid 'IN' invoice found
                return valid_invoices[0]
                
            # Fallback: if no matches start with 'IN', but we found something else, return the last one
            return all_matches[-1].strip()
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return None
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return None
        finally:
            # Clean up the temp file
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass
