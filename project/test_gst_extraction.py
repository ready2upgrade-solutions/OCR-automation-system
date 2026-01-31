import json
from core.extractor import extract_document_text
from core.extractors.gst_certi import extract_gst_certificate_fields

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

    output_path = os.path.join(output_dir, f"gst_output.json")
    result = extract_gst_certificate_fields(raw_text)
    # raw = run_pan_extraction(pdf_path)
    # print(raw)
    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    

    print(f"[OK] JSON saved to: {output_path}")

    return result


if __name__ == "__main__":
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\koncem products\GST REGISTARTION CERTIFICATE.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\Marbella trandz\9. Marbella -GST Certi.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\sygnia brandworks llp\GST Certificate.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\SHREEDHAR ENTERPRISE\GST Certificate.PDF"
    PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\STELLINOX STAINLESS\GST_Certificate.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\goalseek shared service\26. GST Certificate.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\arkmouldtech\GST.pdf" # additional places not extracted
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\goalseek shared service\26. GST Certificate.pdf"
    # PAN_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\sdmi\GST.pdf"

    output = run_pan_extraction(PAN_PDF_PATH)

end = time.perf_counter()

print(f"Inference Time: {end - start:.6f} seconds")

