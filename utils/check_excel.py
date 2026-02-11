from openpyxl import load_workbook
import sys

def check_excel_columns():
    try:
        wb = load_workbook('faktur pajak.xlsx')
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        print("Columns found:")
        for i, header in enumerate(headers):
            print(f"- {header}")
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    check_excel_columns()
