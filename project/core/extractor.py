# from core.pdf_text import extract_pdf_text
# from core.text_normalizer import normalize_text

# def extract_document_text(pdf_path):
#     pdf_pages = extract_pdf_text(pdf_path)

#     has_text = any(p["text"].strip() for p in pdf_pages)

#     if has_text:
#         return [
#             {
#                 "page": p["page"],
#                 "source": "pdf",
#                 "text": normalize_text(p["text"])
#             }
#             for p in pdf_pages
#         ]

#     # fallback to OCR
#     from core.ocr_engine import extract_ocr_text
#     return [
#         {
#             "page": p["page"],
#             "source": "ocr",
#             "text": normalize_text(p["text"])
#         }
#         for p in extract_ocr_text(pdf_path)
#     ]
from core.pdf_text import extract_pdf_text
from core.text_normalizer import normalize_text
import re


def is_text_usable(text: str) -> bool:
    """
    Determines whether extracted PDF text is meaningful.
    """
    text = text.strip()

    if len(text) < 50:
        return False

    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)

    if alpha_ratio < 0.4:
        return False

    return True


def extract_document_text(pdf_path):
    pdf_pages = extract_pdf_text(pdf_path)

    usable_pages = [
        p for p in pdf_pages
        if is_text_usable(p.get("text", ""))
    ]

    if usable_pages:
        return [
            {
                "page": p["page"],
                "source": "pdf",
                "text": normalize_text(p["text"])
            }
            for p in usable_pages
        ]

    # ✅ Force OCR fallback when PDF text is junk
    from core.ocr_engine import extract_ocr_text
    return [
        {
            "page": p["page"],
            "source": "ocr",
            "text": normalize_text(p["text"])
        }
        for p in extract_ocr_text(pdf_path)
    ]
