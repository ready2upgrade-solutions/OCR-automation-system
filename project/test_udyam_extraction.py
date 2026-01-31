
 
import json
import os
from core.extractor import extract_document_text
from core.extractors.udhyam_certi import extract_udyam_fields


def run_udyam_extraction(pdf_path: str, output_dir: str = "output"):
    """Extract Udyam certificate data from PDF and save to JSON."""
    # Extract text from PDF
    pages = extract_document_text(pdf_path)
    raw_text = " ".join(page["text"] for page in pages)
    
    # Extract structured data
    result = extract_udyam_fields(raw_text)
    output_dir = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\project\output"
    
    # Generate filename from PDF
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f"udyam_output.json")
    
    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON saved to: {output_path}")
    return result, output_path


if __name__ == "__main__":
    UDYAM_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\STELLINOX STAINLESS\Udyam_Registration_Certificate_with_annexure.pdf"
    # UDYAM_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\testing_data\SHREEDHAR ENTERPRISE\Print  Udyam Registration Certificate.PDF"
    
    # Extract and save JSON
    result, json_path = run_udyam_extraction(UDYAM_PDF_PATH)
    
    # Optional: Print summary
    print("\n📋 Extraction Summary:")
    print(f"  Enterprise: {result['fields'].get('enterprise_name', 'N/A')}")
    print(f"  Udyam No: {result['fields'].get('udyam_number', 'N/A')}")
    print(f"  Classification Records: {len(result['tables']['classification_history'])}")
    print(f"  Investment Records: {len(result['tables']['investment_details'])}")
    print(f"  NIC Codes: {len(result['tables']['nic_codes'])}")

