import PyPDF2
from PIL import Image
import pytesseract
import io
import fitz  # PyMuPDF
import os

class PDFTextExtractor:
    """
    A comprehensive PDF text extractor that handles:
    - Regular text from PDF
    - Text from images embedded in PDF using OCR
    """
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.all_text = []
        
    def extract_text_pypdf2(self):
        """Extract text using PyPDF2"""
        text_content = []
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"\n--- Page {page_num + 1} (Text) ---\n{text}")
        except Exception as e:
            print(f"Error extracting text with PyPDF2: {e}")
        return text_content
    
    def extract_images_and_text(self):
        """Extract images from PDF and perform OCR on them"""
        image_text_content = []
        try:
            pdf_document = fitz.open(self.pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                images = page.get_images(full=True)
                
                if images:
                    print(f"Found {len(images)} image(s) on page {page_num + 1}")
                
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert to PIL Image
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Perform OCR
                    ocr_text = pytesseract.image_to_string(image)
                    
                    if ocr_text.strip():
                        image_text_content.append(
                            f"\n--- Page {page_num + 1}, Image {img_index + 1} (OCR) ---\n{ocr_text}"
                        )
            
            pdf_document.close()
        except Exception as e:
            print(f"Error extracting images: {e}")
        
        return image_text_content
    
    def extract_all(self):
        """Extract all text from PDF including OCR from images"""
        print(f"Processing PDF: {self.pdf_path}\n")
        
        # Extract regular text
        print("Extracting text from PDF...")
        text_content = self.extract_text_pypdf2()
        self.all_text.extend(text_content)
        
        # Extract and OCR images
        print("Extracting and processing images...")
        image_text = self.extract_images_and_text()
        self.all_text.extend(image_text)
        
        return "\n".join(self.all_text)
    
    def save_to_file(self, output_path):
        """Save extracted text to a file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.all_text))
            print(f"\nText saved to: {output_path}")
        except Exception as e:
            print(f"Error saving file: {e}")


def main():
    """Main function to run the PDF text extractor"""
    
    # Example usage
    pdf_file = "your_document.pdf"  # Replace with your PDF path
    
    # Check if file exists
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found!")
        print("\nPlease update the 'pdf_file' variable with your PDF path.")
        return
    
    # Create extractor instance
    extractor = PDFTextExtractor(pdf_file)
    
    # Extract all text
    all_text = extractor.extract_all()
    
    # Print extracted text
    print("\n" + "="*50)
    print("EXTRACTED TEXT")
    print("="*50)
    print(all_text)
    
    # Save to file
    output_file = pdf_file.replace('.pdf', '_extracted.txt')
    extractor.save_to_file(output_file)
    
    print(f"\n✓ Extraction complete!")
    print(f"Total characters extracted: {len(all_text)}")


if __name__ == "__main__":
    main()