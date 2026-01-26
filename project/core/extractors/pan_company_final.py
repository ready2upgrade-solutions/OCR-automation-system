import re
from typing import Dict
from core.extractor import extract_document_text


def extract_pan_company_fields(raw_text: str) -> dict:
    """Extract PAN Company fields with DEBUG output."""
    text = raw_text.upper()
    data = {
        "document_type": "PAN",
        "fields": {},
        "missing_fields": [],
        "debug": {
            "raw_text_length": len(raw_text),
            "text_preview": raw_text[:200] if raw_text else "EMPTY OCR"
        }
    }
    
    print(f"📏 Text length: {len(raw_text)} chars")
    
    # ========== PAN NUMBER ==========
    pan_patterns = [
        r"\b([A-Z]{5}\d{4}[A-Z])\b",
        r"PAN\s*:?\s*([A-Z]{5}\d{4}[A-Z])",
        r"([A-Z]{5}\d{4}[A-Z])\s*/?\s*[A-Z]{0,3}",
        r"PERMANENT ACCOUNT NUMBER\s*:?\s*([A-Z]{5}\d{4}[A-Z])",
        r"([A-HJKMNPR-Z]{5}[0-9]{4}[A-HJKMNPR-Z])",  # Full PAN charset
    ]
    
    for pattern in pan_patterns:
        m = re.search(pattern, text)
        if m:
            data["fields"]["pan"] = m.group(1)
            print(f"✅ PAN found: {data['fields']['pan']}")
            break
    else:
        data["missing_fields"].append("pan")
        print("❌ No PAN pattern matched")
    
    # ========== COMPANY NAME (IMPROVED) ==========
    company_blacklist = [
        "INCOME TAX", "DEPARTMENT", "GOVT", "GOVERNMENT", "INDIA", "MINISTRY"
    ]

    company_keywords = [
        "PRIVATE", "LIMITED", "PVT", "LTD","LLP","COMPANY","CORPORATION"
    ]

    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 5]

    def is_valid_company(line: str) -> bool:
        if any(bad in line for bad in company_blacklist):
            return False
        if any(key in line for key in company_keywords):
            return True
        return False

    company_name = None

    # 1️⃣ Prefer lines AFTER PAN
    if "pan" in data["fields"]:
        pan_match = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
        if pan_match:
            after_pan_text = text[pan_match.end():]
            for line in after_pan_text.splitlines():
                line = line.strip()
                if is_valid_company(line):
                    company_name = re.sub(r"[^A-Z\s&\.]", "", line)
                    break

    # 2️⃣ Fallback: anywhere in document
    if not company_name:
        for line in lines:
            if is_valid_company(line):
                company_name = re.sub(r"[^A-Z\s&\.]", "", line)
                break

    if company_name:
        data["fields"]["name"] = clean_company_name(company_name)
    else:
        data["missing_fields"].append("name")

    
        # ========== DATE OF INCORPORATION ==========
    inc_date = extract_incorporation_date(text)

    if inc_date:
        data["fields"]["incorporation_date"] = inc_date
    else:
        data["missing_fields"].append("incorporation_date")

    data["missing_fields"] = list(set(data["missing_fields"]))

    return data


def clean_company_name(name: str) -> str:
    """
    Removes OCR noise AFTER legal company suffix safely
    """
    name = name.strip()

    # Normalize spaces
    name = re.sub(r"\s+", " ", name)

    # Legal suffixes (ordered by priority)
    legal_suffixes = [
        "PRIVATE LIMITED",
        "PVT LTD",
        "PRIVATE LTD",
        "LIMITED",
        "LTD"
    ]

    for suffix in legal_suffixes:
        if suffix in name:
            # Cut everything AFTER the suffix
            idx = name.find(suffix) + len(suffix)
            return name[:idx].strip()

    # Fallback: remove trailing noise tokens
    name = re.sub(r"\b[A-Z]{1,3}\d{0,3}$", "", name).strip()

    return name

def extract_incorporation_date(text: str) -> str | None:
    """
    Extracts date of incorporation from PAN OCR text.
    Accepts common OCR-safe date formats.
    """

    date_patterns = [
        r"\b(0[1-9]|[12][0-9]|3[01])[\/\-\.](0[1-9]|1[0-2])[\/\-\.]((19|20)\d{2})\b",
        r"\b((19|20)\d{2})[\/\-\.](0[1-9]|1[0-2])[\/\-\.](0[1-9]|[12][0-9]|3[01])\b"
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)

    return None
