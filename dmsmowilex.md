# Playwright Automation Project (Python + Poetry + Pytest + POM)

Buatkan project automation testing menggunakan:

- **Playwright (Python)**
- **Poetry** untuk dependency management
- **Pytest** sebagai test runner
- **Page Object Model (POM)**
- Support debugging menggunakan **Chrome MCP** (untuk kebutuhan debugging/inspection)

Base URL aplikasi:
**https://dms.mowilex.id/**

---

## ⚠️ IMPORTANT (PRODUCTION ENVIRONMENT)

Aplikasi ini adalah **PRODUCTION**, jadi scope automation harus sangat terbatas.

**JANGAN melakukan hal lain di luar requirement ini.**
Tidak boleh ada exploratory test, tidak boleh akses menu lain, tidak boleh create/update/delete data, dan tidak boleh action tambahan apa pun.

---

## ✅ Scope yang Diizinkan (WAJIB DIPATUHI)

Automation hanya boleh mencakup:

- Masuk ke menu **Faktur Pajak**
- Filter **Status Invoice = "Not Match"**
- Klik tombol **Download** pada setiap row
- Jika hasil download adalah **Not Found**, tulis **kode faktur pajak** ke file `.txt`

---

## ❌ Scope yang Dilarang (TIDAK BOLEH)

- Tidak boleh mengakses menu lain selain **Faktur Pajak**
- Tidak boleh test fitur lain selain download faktur pajak
- Tidak boleh melakukan create/update/delete/approve/reject data
- Tidak boleh submit form lain atau trigger action selain filter + download
- Tidak boleh menambahkan test tambahan apa pun

---

## Test Case: Faktur Pajak - Download untuk Status "Not Match"

### Steps

1. Login ke aplikasi menggunakan credential yang diberikan.
2. Masuk ke menu **Faktur Pajak**.
3. Pada halaman Faktur Pajak, lakukan filter:
   - **Status Invoice = "Not Match"**
4. Setelah tabel data muncul, lakukan iterasi untuk setiap row faktur pajak:
   - Klik tombol **Download**
5. Jika setelah klik Download hasilnya adalah **Not Found** (file tidak tersedia / error message muncul):
   - Ambil **kode faktur pajak** dari row tersebut
   - Simpan kode tersebut ke file:
     - `not_found_faktur_pajak.txt`
   - Simpan dengan format **append** (tidak overwrite)
   - Format file: **1 kode per baris**
6. Jangan tulis kode faktur pajak lain selain yang download-nya benar-benar Not Found.

---

## Credential

Gunakan login berikut:

- Username: `admin@local.test`
- Password: `AdminPass123`

Catatan:
- Sebaiknya credential disimpan di `.env` dan dibaca menggunakan environment variable.
- Jangan hardcode credential di source code.

---

## Struktur Project yang Diinginkan

Project harus rapi dengan struktur seperti berikut:

- `pages/` → POM classes (LoginPage, FakturPajakPage, dll)
- `tests/` → test files
- `utils/` → helper utilities (file writer, wait helper, dsb)
- `conftest.py` → pytest fixtures (browser setup, page, base url)
- konfigurasi base url terpusat

Contoh nama test file:
- `tests/test_faktur_pajak_download_not_match.py`

---

## Debugging Requirement (Chrome MCP)

Tambahkan dukungan debugging menggunakan **Chrome MCP**, misalnya dengan:

- opsi menjalankan test dengan mode debug/headed
- connect ke Chrome via CDP jika diperlukan
- dokumentasi cara menjalankan debug (misalnya: `PWDEBUG=1`, `--headed`, atau connect MCP)

Tujuannya agar mudah melakukan debugging saat test berjalan.

---

## Output yang Diharapkan

- Source code lengkap project sesuai struktur di atas
- Konfigurasi Poetry (`pyproject.toml`)
- Dokumentasi cara install & menjalankan test
- Output file `not_found_faktur_pajak.txt` otomatis dibuat jika belum ada
- Hanya melakukan action sesuai scope (menu Faktur Pajak + filter Not Match + download + log Not Found)
