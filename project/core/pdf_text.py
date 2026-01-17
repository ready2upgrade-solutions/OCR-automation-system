import fitz  # PyMuPDF


def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        text = page.get_text("text")

        pages.append({
            "page": page.number + 1,
            "text": text.strip()
        })

    return pages
