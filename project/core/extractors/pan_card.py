import re
from typing import Dict
from core.extractor import extract_document_text

def get_pan_holder_type(pan: str) -> str | None:
    """
    Determines PAN holder type from 4th character.
    """
    if len(pan) != 10:
        return None

    pan_type_map = {
        "P": "PERSON",
        "C": "COMPANY",
        "F": "FIRM",
        "L": "LLP",
        "T": "TRUST",
        "H": "HUF",
        "A": "AOP",
        "B": "BOI",
        "J": "ARTIFICIAL_JURIDICAL_PERSON",
        "G": "GOVERNMENT"
    }

    return pan_type_map.get(pan[3])

def extract_person_name(text: str, pan: str) -> str | None:
    """
    Robust extraction of individual PAN holder name.
    Tries AFTER PAN first, then BEFORE PAN.
    """

    blacklist = [
        "INCOME TAX", "DEPARTMENT", "GOVT", "GOVERNMENT",
        "INDIA", "CARD", "NUMBER", "PERMANENT"
    ]

    pan_match = re.search(rf"\b{pan}\b", text)
    if not pan_match:
        return None

    def is_valid_name(line: str) -> bool:
        if any(bad in line for bad in blacklist):
            return False

        if not re.fullmatch(r"[A-Z\s\.]+", line):
            return False

        words = line.split()

        if not (2 <= len(words) <= 4):
            return False

        if any(len(w) < 3 for w in words):
            return False

        if len(line) < 10:
            return False

        return True

    # ---------- 1️⃣ TRY AFTER PAN ----------
    after_pan = text[pan_match.end():]
    for line in after_pan.splitlines():
        line = line.strip()

        if "FATHER" in line:
            break

        if is_valid_name(line):
            return re.sub(r"\s+", " ", line)

    # ---------- 2️⃣ FALLBACK: BEFORE PAN ----------
    before_pan = text[:pan_match.start()]
    before_lines = before_pan.splitlines()

    for line in reversed(before_lines):
        line = line.strip()

        if "FATHER" in line:
            break

        if is_valid_name(line):
            return re.sub(r"\s+", " ", line)

    return None

def extract_pan_company_fields(raw_text: str) -> dict:
    """Extract PAN fields with person/company logic."""
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

    # ========== PAN NUMBER ==========
    pan_patterns = [
        r"\b([A-Z]{5}\d{4}[A-Z])\b",
        r"PAN\s*:?\s*([A-Z]{5}\d{4}[A-Z])",
        r"PERMANENT ACCOUNT NUMBER\s*:?\s*([A-Z]{5}\d{4}[A-Z])",
        r"([A-HJKMNPR-Z]{5}[0-9]{4}[A-HJKMNPR-Z])"
    ]

    for pattern in pan_patterns:
        m = re.search(pattern, text)
        if m:
            pan = m.group(1)
            data["fields"]["pan"] = pan
            data["fields"]["pan_type"] = get_pan_holder_type(pan)
            break
    else:
        data["missing_fields"].append("pan")

    pan_type = data["fields"].get("pan_type")

    # ========== NAME EXTRACTION ==========
    if pan_type == "COMPANY":
        company_blacklist = [
            "INCOME TAX", "DEPARTMENT", "GOVT", "GOVERNMENT", "INDIA", "MINISTRY"
        ]

        company_keywords = [
            "PRIVATE", "LIMITED", "PVT", "LTD", "LLP", "COMPANY", "CORPORATION"
        ]

        def is_valid_company(line: str) -> bool:
            if any(bad in line for bad in company_blacklist):
                return False
            return any(key in line for key in company_keywords)

        company_name = None

        pan_match = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
        if pan_match:
            after_pan = text[pan_match.end():]
            for line in after_pan.splitlines():
                if is_valid_company(line):
                    company_name = re.sub(r"[^A-Z\s&\.]", "", line)
                    break

        if not company_name:
            for line in text.splitlines():
                if is_valid_company(line):
                    company_name = re.sub(r"[^A-Z\s&\.]", "", line)
                    break

        if company_name:
            data["fields"]["name"] = clean_company_name(company_name)
        else:
            data["missing_fields"].append("name")

    elif pan_type == "PERSON":
        person_name = extract_person_name(text, data["fields"]["pan"])
        if person_name:
            data["fields"]["name"] = person_name
        else:
            data["missing_fields"].append("name")

    else:
        data["missing_fields"].append("name")

    # ========== DATE OF INCORPORATION ==========
    inc_date = extract_incorporation_date(text)
    if inc_date:
        data["fields"]["incorporation_date"] = inc_date
    else:
        data["missing_fields"].append("incorporation_date")

    # De-duplicate
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
