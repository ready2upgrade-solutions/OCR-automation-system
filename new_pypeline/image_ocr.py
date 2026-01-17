from paddleocr import PaddleOCR
import cv2

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


def run_ocr(image_bgr):
    image_bgr = safe_resize(image_bgr)

    try:
        result = ocr.ocr(image_bgr)
    except Exception as e:
        print("⚠️ OCR failed:", e)
        return []

    if not result or not isinstance(result, list):
        return []

    page = result[0]
    texts = page.get("rec_texts", [])
    scores = page.get("rec_scores", [])

    lines = []
    for i, txt in enumerate(texts):
        score = scores[i] if i < len(scores) else 1.0
        if score > 0.25 and txt.strip():
            lines.append(txt)

    return lines
