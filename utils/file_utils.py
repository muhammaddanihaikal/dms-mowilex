import os

MONTH_MAP = {
    "01": "januari",
    "02": "februari",
    "03": "maret",
    "04": "april",
    "05": "mei",
    "06": "juni",
    "07": "juli",
    "08": "agustus",
    "09": "september",
    "10": "oktober",
    "11": "november",
    "12": "desember"
}

def get_filename_by_date(date_str):
    # date_str format: YYYY-MM-DD
    year = date_str[:4]
    month_num = date_str[5:7]
    month_name = MONTH_MAP.get(month_num, "unknown")
    return f"not_found_faktur_pajak_{month_name}_{year}.txt"

def append_to_not_found_file(code, upload_date):
    filename = get_filename_by_date(upload_date)
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(f"===not_found_{upload_date[5:7]}_{upload_date[:4]}===\n")
    
    with open(filename, "a") as f:
        f.write(f"{code}\n")

def write_header_to_not_found_file(header_date):
    filename = get_filename_by_date(header_date)
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(f"===not_found_{header_date[5:7]}_{header_date[:4]}===\n")
            
    with open(filename, "a") as f:
        f.write(f"\n==={header_date}===\n")
