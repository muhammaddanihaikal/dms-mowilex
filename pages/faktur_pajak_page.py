from playwright.sync_api import Page, expect

class FakturPajakPage:
    def __init__(self, page: Page):
        self.page = page
        self.menu_attachment_documents = page.get_by_role("button", name="Attachment Documents")
        self.menu_faktur_pajak = page.get_by_role("link", name="Faktur Pajak")
        
        # Filter elements
        self.filter_button = page.get_by_role("button", name="Filter")
        self.status_invoice_select = page.get_by_role("combobox", name="Status Invoices")
        
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

    def get_all_rows(self):
        # We need to find the rows in the table body
        return self.page.locator("table.fi-ta-table tbody tr").all()

    def get_faktur_pajak_code(self, row):
        # Column 0 is 'No', Column 1 is 'Faktur Pajak Code'
        return row.locator("td").nth(1).inner_text().strip()

    def get_invoice_number(self, row):
        # Column 2 is 'Invoice Number'
        return row.locator("td").nth(2).inner_text().strip()

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

    def go_to_next_page(self):
        next_button = self.page.get_by_role("button", name="Next")
        next_button.click()
        self.page.wait_for_load_state("networkidle")
