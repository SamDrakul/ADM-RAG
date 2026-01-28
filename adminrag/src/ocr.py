import os
from typing import List
from pdf2image import convert_from_path
import pytesseract
from PIL import ImageOps

TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def ocr_pdf_to_text(pdf_path: str, dpi: int = 300, lang: str = "por") -> str:
    images = convert_from_path(pdf_path, dpi=dpi)
    texts: List[str] = []
    for img in images:
        # preprocess: improves many scans
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        txt = pytesseract.image_to_string(img, lang=lang)
        texts.append(txt)
    return "\n".join(texts).strip()
