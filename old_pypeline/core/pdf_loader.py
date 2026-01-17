# core/pdf_loader.py

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

def load_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        # ---- TEXT LAYER (if exists) ----
        text = page.get_text("text")  # plain text
        text_blocks = page.get_text("dict")["blocks"]  # geometry-aware

        # ---- IMAGE RENDER (always) ----
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_np = np.array(img)  # ✅ OCR-compatible

        pages.append({
            "page": page.number + 1,     # ✅ pipeline expects this
            "text": text.strip(),        # ✅ semantic text
            "text_blocks": text_blocks,  # ✅ geometry
            "image": img_np              # ✅ OCR-safe
        })

    return pages
