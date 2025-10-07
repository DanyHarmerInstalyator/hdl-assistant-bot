# bot/utils/pdf_text_cache.py
import fitz  # pymupdf
from io import BytesIO

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Извлекает текст из PDF, переданного как bytes.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"⚠️ Ошибка при извлечении текста из PDF: {e}")
        return ""