from core.pdf_text import extract_pdf_text
from core.text_normalizer import normalize_text

def extract_document_text(pdf_path):
    pdf_pages = extract_pdf_text(pdf_path)

    has_text = any(p["text"].strip() for p in pdf_pages)

    if has_text:
        return [
            {
                "page": p["page"],
                "source": "pdf",
                "text": normalize_text(p["text"])
            }
            for p in pdf_pages
        ]

    # fallback to OCR
    from core.ocr_engine import extract_ocr_text
    return [
        {
            "page": p["page"],
            "source": "ocr",
            "text": normalize_text(p["text"])
        }
        for p in extract_ocr_text(pdf_path)
    ]
