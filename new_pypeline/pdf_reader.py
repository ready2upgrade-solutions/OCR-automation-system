import fitz
from PIL import Image

def extract_pages_as_images(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)

    pages = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append((i, img))

    return pages
