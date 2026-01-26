import json
from core.extractor import extract_document_text
from core.extractors.pan_company_final import extract_pan_company_fields


def run_pan_extraction(pdf_path: str):
    pages = extract_document_text(pdf_path)
    raw_text = " ".join(page["text"] for page in pages)

    result = extract_pan_company_fields(raw_text)
    return result


if __name__ == "__main__":
    PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\testing_data\PAN_Card_-_Company.pdf"

    output = run_pan_extraction(PAN_PDF_PATH)
    print(json.dumps(output, indent=2))
