# core/ocr_engine.py

from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang="en")

def ocr_page(image_np):
    atoms = []

    results = ocr.ocr(image_np)

    if not results:
        return atoms

    for block in results:
        # New PaddleOCR may return nested blocks
        if isinstance(block, list):
            for line in block:
                atom = parse_line(line)
                if atom:
                    atoms.append(atom)
        else:
            atom = parse_line(block)
            if atom:
                atoms.append(atom)

    return atoms


def parse_line(line):
    """
    Safely parse ANY PaddleOCR output shape
    """

    # Case 1: New dict-style output
    if isinstance(line, dict):
        text = line.get("text", "").strip()
        conf = line.get("score", 1.0)
        bbox = line.get("points", [])

        if text:
            return {
                "text": text,
                "conf": conf,
                "bbox": bbox,
                "source": "ocr"
            }

    # Case 2: Old tuple/list format
    if isinstance(line, (list, tuple)) and len(line) >= 2:
        text_part = line[1]

        if isinstance(text_part, (list, tuple)) and len(text_part) >= 2:
            text = str(text_part[0]).strip()
            conf = float(text_part[1])

            if text:
                return {
                    "text": text,
                    "conf": conf,
                    "bbox": line[0],
                    "source": "ocr"
                }

        # Case 3:
