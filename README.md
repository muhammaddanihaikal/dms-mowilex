# DMS Mowilex Automation - Faktur Pajak Download

Project automation untuk mengunduh Faktur Pajak dengan status "Not Match" dan mencatat file yang tidak ditemukan.

## Persyaratan
- Python 3.10+
- Poetry

## Instalasi

1. Install dependencies menggunakan Poetry:
   ```bash
   poetry install
   ```

2. Install browser Playwright:
   ```bash
   poetry run playwright install chromium
   ```

3. Konfigurasi file `.env`:
   Salin `.env.example` ke `.env` dan isi dengan credential yang benar.
   ```bash
   cp .env.example .env
   ```

## Menjalankan Test

Jalankan test menggunakan pytest:
```bash
poetry run pytest
```

### Debugging
Untuk menjalankan dengan mode debugging (browser terlihat dan berhenti jika ada error):
```bash
poetry run pytest --headed
```
Atau gunakan `PWDEBUG=1`:
```bash
$env:PWDEBUG=1; poetry run pytest
```

## Output
- Kode faktur pajak yang tidak ditemukan akan dicatat di file `not_found_faktur_pajak.txt`.
