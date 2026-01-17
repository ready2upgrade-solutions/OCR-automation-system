# core/atom_builder.py

from core.ocr_engine import ocr_page

def build_atoms(pages):
    atoms = []

    for page in pages:
        page_no = page["page"]

        # ---------- 1. PDF TEXT → ATOMS ----------
        pdf_text = page.get("text", "")
        if pdf_text:
            for line in pdf_text.splitlines():
                line = line.strip()
                if not line:
                    continue

                atoms.append({
                    "page": page_no,
                    "text": line,
                    "conf": 1.0,
                    "bbox": None,
                    "source": "pdf"
                })

        # ---------- 2. OCR TEXT → ATOMS ----------
        image = page.get("image")
        if image is not None:
            try:
                ocr_atoms = ocr_page(image)
                for oa in ocr_atoms:
                    atoms.append({
                        "page": page_no,
                        "text": oa["text"],
                        "conf": oa.get("conf", 1.0),
                        "bbox": oa.get("bbox"),
                        "source": "ocr"
                    })
            except Exception as e:
                print(f"OCR failed on page {page_no}: {e}")

    return atoms
