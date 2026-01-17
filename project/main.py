# from core.extractor import extract_document_text
# import json

# PDF_PATH = r"C:\Users\Meet patel\MEET\projects\ocr\testing_data\Udyam_Registration_Certificate_with_annexure.pdf"

# def main():
#     pages = extract_document_text(PDF_PATH)

#     output = {
#         "total_pages": len(pages),
#         "pages": pages
#     }

#     with open("output/result.json", "w", encoding="utf-8") as f:
#         json.dump(output, f, indent=2, ensure_ascii=False)

#     print("✅ Text extraction completed (PDF + OCR fallback)")

# if __name__ == "__main__":
#     main()

from core.extractor import extract_document_text
from core.extractors.udyam import extract_udyam_fields

PDF_PATH = r"C:\Users\Meet patel\MEET\projects\ocr\testing_data\Udyam_Registration_Certificate_with_annexure.pdf"

def main():
    pages = extract_document_text(PDF_PATH)

    # TEMP: manually choose UDYAM (classifier later)
    udyam_result = extract_udyam_fields(
        raw_text=" ".join(p["text"] for p in pages)
    )

    print(udyam_result)

if __name__ == "__main__":
    main()
