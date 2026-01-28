from pypdf import PdfReader
from ocr import ocr_pdf_to_text

def extract_pdf_text(pdf_path: str) -> str:
    # try normal text extraction
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    text = "\n".join(parts).strip()

    # fallback to OCR for scanned PDFs
    if len(text) < 30:
        text = ocr_pdf_to_text(pdf_path)

    return text.strip()
