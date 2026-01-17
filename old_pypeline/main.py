from core.pdf_loader import load_pdf
from core.atom_builder import build_atoms
from core.geometry import cluster_rows
from core.semantic_builder import build_semantics
from utils.helpers import save_json

PDF_PATH = r"C:\Users\Anjali Patel\Downloads\MRK HEALTHCARE PVT LTD KYC 20260101 iFirm\3. Directors KYC.pdf"

def main():
    pages_data = load_pdf(PDF_PATH)

    atoms = build_atoms(pages_data)

    rows = cluster_rows(atoms)

    facts, text_blocks = build_semantics(rows)

    output = {
        "total_atoms": len(atoms),
        "atoms_source_count": {
            "pdf": sum(1 for a in atoms if a.get("source") == "pdf"),
            "ocr": sum(1 for a in atoms if a.get("source") == "ocr"),
        },
        "key_value_pairs": [
            {
                "page": f.page,
                "label": f.label_text,
                "value": f.value_text
            }
            for f in facts
        ],
        "text_blocks": text_blocks
    }

    save_json(output, "output/result.json")
    print("✅ Extraction complete (PDF + OCR)")

if __name__ == "__main__":
    main()
