# # test_extraction_demo.py
# # Final demo script to test the Udyam extraction with perfect output

# from core.extractor import extract_document_text
# from core.extractors.udyam_updated_final import extract_udyam_fields
# import json
# import os

# PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\testing_data\Udyam_Registration_Certificate_with_annexure.pdf"

# def main():
#     print("\n" + "="*80)
#     print("🚀 STARTING UDYAM CERTIFICATE EXTRACTION")
#     print("="*80)
#     print(f"📄 Processing: {os.path.basename(PDF_PATH)}")
#     print()

#     # Extract text from PDF
#     print("⏳ Step 1: Extracting text from PDF using OCR...")
#     pages = extract_document_text(PDF_PATH)
#     raw_text = " ".join(p["text"] for p in pages)
#     print(f"✅ Extracted {len(pages)} pages")

#     # Extract all fields and tables
#     print("⏳ Step 2: Extracting structured data using regex...")
#     udyam_result = extract_udyam_fields(raw_text)
#     print("✅ Extraction complete")
#     print()

#     # Pretty print the results
#     print("="*80)
#     print("📋 UDYAM CERTIFICATE EXTRACTION RESULTS")
#     print("="*80)

#     print("\n📌 BASIC FIELDS:")
#     print("-"*80)
#     for key, value in udyam_result["fields"].items():
#         if key == "official_address":
#             continue  # Skip, will display separately
#         print(f"   {key:30s}: {value}")

#     # Display Official Address with beautiful formatting
#     print("\n🏢 OFFICIAL ADDRESS OF ENTERPRISE:")
#     print("-"*80)
#     addr = udyam_result["fields"].get("official_address", {})
#     if addr:
#         addr_labels = {
#             "flat_no": "Flat/Door/Block No.",
#             "building": "Building Name",
#             "village_town": "Village/Town",
#             "block": "Block",
#             "road": "Road/Street/Lane",
#             "city": "City",
#             "state": "State",
#             "district": "District",
#             "pin": "PIN Code",
#             "mobile": "Mobile",
#             "email": "Email"
#         }
#         for key, label in addr_labels.items():
#             if key in addr:
#                 print(f"   {label:25s}: {addr[key]}")
#     else:
#         print("   ⚠️  No address data extracted")

#     print("\n\n📊 EXTRACTED TABLES:")
#     print("="*80)

#     # 1. Classification History
#     if udyam_result["tables"]["classification_history"]:
#         print("\n1️⃣  CLASSIFICATION HISTORY:")
#         print("-"*80)
#         for i, record in enumerate(udyam_result["tables"]["classification_history"], 1):
#             print(f"   {i}. Year: {record['classification_year']:10s} | Type: {record['enterprise_type']:6s} | Date: {record['classification_date']}")
#     else:
#         print("\n1️⃣  CLASSIFICATION HISTORY: No data")

#     # 2. Employment Details
#     print("\n2️⃣  EMPLOYMENT DETAILS:")
#     print("-"*80)
#     emp = udyam_result["tables"]["employment_details"]
#     if emp:
#         print(f"   Male    : {emp.get('male', 0):3d}")
#         print(f"   Female  : {emp.get('female', 0):3d}")
#         print(f"   Other   : {emp.get('other', 0):3d}")
#         print(f"   ────────────────")
#         print(f"   Total   : {emp.get('total', 0):3d}")
#     else:
#         print("   ⚠️  No employment data extracted")

#     # 3. Investment Details
#     print("\n3️⃣  INVESTMENT & TURNOVER DETAILS:")
#     print("-"*80)
#     if udyam_result["tables"]["investment_details"]:
#         for record in udyam_result["tables"]["investment_details"]:
#             print(f"   📅 Financial Year: {record['financial_year']}")
#             print(f"      Enterprise Type    : {record['enterprise_type']}")
#             print(f"      Net Investment     : ₹ {record['net_investment']:,.2f}")
#             print(f"      Total Turnover     : ₹ {record['total_turnover']:,.2f}")
#             print(f"      Export Turnover    : ₹ {record['export_turnover']:,.2f}")
#             print(f"      Net Turnover       : ₹ {record['net_turnover']:,.2f}")
#             print(f"      ITR Filed          : {record['itr_filled']}")
#             print(f"      ITR Type           : {record['itr_type']}")
#             print()
#     else:
#         print("   ⚠️  No investment data extracted")

#     # 4. Units Details
#     print("4️⃣  UNIT(S) DETAILS:")
#     print("-"*80)
#     if udyam_result["tables"]["units_details"]:
#         for i, unit in enumerate(udyam_result["tables"]["units_details"], 1):
#             print(f"   Unit {i}:")
#             for key, value in unit.items():
#                 print(f"      {key:15s}: {value}")
#             print()
#     else:
#         print("   ⚠️  No units data extracted")

#     # 5. NIC Codes
#     print("5️⃣  NATIONAL INDUSTRY CLASSIFICATION (NIC) CODES:")
#     print("-"*80)
#     if udyam_result["tables"]["nic_codes"]:
#         for nic in udyam_result["tables"]["nic_codes"]:
#             print(f"   {nic['sno']}. {nic['nic_2_digit']}")
#             print(f"      └─ {nic['nic_4_digit']}")
#             print(f"         └─ {nic['nic_5_digit']}")
#             print(f"         Activity: {nic['activity']}")
#             print()
#     else:
#         print("   ⚠️  No NIC codes extracted")

#     # 6. Bank Details - BEAUTIFUL DISPLAY
#     print("6️⃣  BANK DETAILS:")
#     print("-"*80)
#     bank = udyam_result["tables"]["bank_details"]
#     if bank:
#         print(f"   Bank Name          : {bank.get('bank_name', 'N/A')}")
#         print(f"   IFSC Code          : {bank.get('ifsc_code', 'N/A')}")
#         print(f"   Account Number     : {bank.get('account_number', 'N/A')}")
#     else:
#         print("   ⚠️  No bank details extracted")

#     # Validation Flags
#     if udyam_result["flags"]:
#         print("\n\n⚠️  VALIDATION FLAGS:")
#         print("="*80)
#         for flag in udyam_result["flags"]:
#             print(f"   🚩 {flag}")

#     # Save to JSON
#     print("\n" + "="*80)
#     output_path = "output/udyam_extraction_result.json"
#     try:
#         os.makedirs("output", exist_ok=True)
#         with open(output_path, "w", encoding="utf-8") as f:
#             json.dump(udyam_result, f, indent=2, ensure_ascii=False)
#         print(f"✅ Full extraction saved to: {output_path}")
#     except Exception as e:
#         print(f"⚠️  Could not save to file: {e}")

#     print("="*80)
#     print("🎉 EXTRACTION COMPLETED SUCCESSFULLY!")
#     print("="*80)

# if __name__ == "__main__":
#     main()
 
import json
import os
from core.extractor import extract_document_text
from core.extractors.udyam_updated_final import extract_udyam_fields


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
    UDYAM_PDF_PATH = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\testing_data\Udyam_Registration_Certificate_with_annexure.pdf"
    
    # Extract and save JSON
    result, json_path = run_udyam_extraction(UDYAM_PDF_PATH)
    
    # Optional: Print summary
    print("\n📋 Extraction Summary:")
    print(f"  Enterprise: {result['fields'].get('enterprise_name', 'N/A')}")
    print(f"  Udyam No: {result['fields'].get('udyam_number', 'N/A')}")
    print(f"  Classification Records: {len(result['tables']['classification_history'])}")
    print(f"  Investment Records: {len(result['tables']['investment_details'])}")
    print(f"  NIC Codes: {len(result['tables']['nic_codes'])}")
