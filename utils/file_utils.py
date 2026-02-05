import os

def append_to_not_found_file(code, filename="not_found_faktur_pajak.txt"):
    # Ensure directory exists or just write in current dir as requested
    with open(filename, "a") as f:
        f.write(f"{code}\n")
