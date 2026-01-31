import json
from core.extractor import extract_document_text
from core.extractors.pan_card import extract_pan_company_fields

import os
os.environ["FLAGS_use_onednn"] = "false"

import time

def inference():
    time.sleep(0.3)
    return "output"

start = time.perf_counter()
result = inference()

def run_pan_extraction(pdf_path: str):
    pages = extract_document_text(pdf_path)
    raw_text = " ".join(page["text"] for page in pages)
    output_dir = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\project\output"

    output_path = os.path.join(output_dir, f"pan_output.json")
    result = extract_pan_company_fields(raw_text)
    # raw = run_pan_extraction(pdf_path)
    # print(raw)
    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    

    print(f"✅ JSON saved to: {output_path}")

    return result


if __name__ == "__main__":
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\koncem products\20. Company PAN.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\sygnia brandworks llp\Company PAN.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\SHREEDHAR ENTERPRISE\Shreedhar PAN card.pdf" # director 
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\goalseek shared service\20. Company PAN.pdf"
    PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\STELLINOX STAINLESS\PAN_Card_-_Company.pdf"

    output = run_pan_extraction(PAN_PDF_PATH)

end = time.perf_counter()

print(f"Inference Time: {end - start:.6f} seconds")

