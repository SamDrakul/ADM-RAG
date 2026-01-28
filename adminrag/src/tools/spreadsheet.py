from openpyxl import Workbook

HEADERS = [
    "file_name","doc_type","cpf","payer_name","beneficiary",
    "linha_digitavel","barcode","total_value","payment_status","payment_date","auth_code","notes"
]

def export_xlsx(records: list, out_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "docs"
    ws.append(HEADERS)
    for r in records:
        ws.append([r.get(h) for h in HEADERS])
    wb.save(out_path)
    return {"ok": True, "xlsx": out_path}
