from paddleocr import PaddleOCR
import fitz  # PyMuPDF
import cv2
import numpy as np

ocr = PaddleOCR(
    lang="en",
    use_textline_orientation=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False
)

def safe_resize(img, max_side=2500):
    h, w = img.shape[:2]
    scale = min(max_side / h, max_side / w, 1.0)

    if scale < 1.0:
        img = cv2.resize(
            img,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )
    return img


def extract_ocr_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]

        # Render page to image using PyMuPDF (NO poppler)
        pix = page.get_pixmap(dpi=300)
        img = np.frombuffer(pix.samples, dtype=np.uint8)
        img = img.reshape(pix.height, pix.width, pix.n)

        if pix.n == 4:  # RGBA → BGR
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        img = safe_resize(img)

        try:
            result = ocr.ocr(img)
        except Exception as e:
            print("⚠️ OCR failed:", e)
            continue

        if not result or not isinstance(result, list):
            continue

        page_data = result[0]
        texts = page_data.get("rec_texts", [])
        scores = page_data.get("rec_scores", [])

        lines = []
        for i, txt in enumerate(texts):
            score = scores[i] if i < len(scores) else 1.0
            if score > 0.25 and txt.strip():
                lines.append(txt)

        pages.append({
            "page": page_index + 1,
            "source": "ocr",
            "text": "\n".join(lines)
        })

    return pages
