from pdf_reader import extract_pages_as_images
from preprocess import preprocess_image
from image_ocr import run_ocr
from utils import basic_cleanup

def process_pdf(pdf_path):
    pages = extract_pages_as_images(pdf_path)
    output = []

    for page_no, pil_img in pages:
        processed = preprocess_image(pil_img)
        lines = run_ocr(processed)
        lines = basic_cleanup(lines)

        output.append(f"\n===== PAGE {page_no} =====")
        output.extend(lines if lines else ["[NO TEXT FOUND]"])

    return "\n".join(output)

if __name__ == "__main__":
    pdf_path = r"C:\Users\Meet patel\MEET\projects\ocr\testing_data\Kartikbhai_-_Aadhar_Card.pdf"
    text = process_pdf(pdf_path)

    with open("new_pypeline/output.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ OCR completed")
