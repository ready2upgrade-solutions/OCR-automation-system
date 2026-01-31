import json
import re
from typing import Dict, List

# ---------------------------
# Utility Normalizers
# ---------------------------

def normalize_text(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"[^A-Z0-9 ]", "", value.upper()).strip()


def normalize_pan(pan: str) -> str:
    return pan.strip().upper() if pan else ""


def normalize_address(addr: Dict) -> Dict:
    return {
        "city": normalize_text(addr.get("city", "")),
        "district": normalize_text(addr.get("district", "")),
        "state": normalize_text(addr.get("state", "")),
        "pin": addr.get("pin_code") or addr.get("pin", "")
    }


# ---------------------------
# Document Adapters
# ---------------------------

def pan_adapter(pan_data: Dict) -> Dict:
    fields = pan_data.get("fields", {})
    return {
        "legal_name": normalize_text(fields.get("name", "")),
        "pan": normalize_pan(fields.get("pan", "")),
        "source": "PAN"
    }


def gst_adapter(gst_data: Dict) -> Dict:
    fields = gst_data.get("fields", {})
    return {
        "legal_name": normalize_text(fields.get("name", "")),
        "constitution": normalize_text(fields.get("constitution_of_business", "")),
        "pan": normalize_pan(fields.get("gst_number", "")[2:12]),
        "principal_address": normalize_address(fields.get("principal_address", {})),
        "source": "GST"
    }


def udyam_adapter(udyam_data: Dict) -> Dict:
    fields = udyam_data.get("fields", {})
    return {
        "legal_name": normalize_text(fields.get("enterprise_name", "")),
        "pan": normalize_pan(fields.get("pan", "")),
        "incorporation_date": fields.get("incorporation_date"),
        "commencement_date": fields.get("commencement_date"),
        "registered_address": normalize_address(fields.get("official_address", {})),
        "source": "UDYAM"
    }


# ---------------------------
# Canonical Entity Builder
# ---------------------------

def build_entity(pan, gst, udyam) -> Dict:
    return {
        "pan": pan,
        "gst": gst,
        "udyam": udyam
    }


# ---------------------------
# Rule Engine
# ---------------------------

def rule_name_match(entity: Dict, doc_a: str, doc_b: str) -> Dict:
    name_a = entity[doc_a].get("legal_name", "")
    name_b = entity[doc_b].get("legal_name", "")

    status = "PASS" if name_a and name_a == name_b else "FAIL"

    return {
        "rule": f"NAME_MATCH_{doc_a}_{doc_b}",
        "status": status,
        "details": f"{doc_a} name vs {doc_b} name"
    }


def rule_pan_match(entity: Dict, doc: str) -> Dict:
    pan_main = entity["pan"].get("pan", "")
    pan_other = entity[doc].get("pan", "")

    status = "PASS" if pan_main and pan_main == pan_other else "FAIL"

    return {
        "rule": f"PAN_MATCH_PAN_{doc}",
        "status": status,
        "details": f"PAN vs {doc} PAN"
    }


def rule_address_match(addr_a: Dict, addr_b: Dict, label: str) -> Dict:
    score = 0
    if addr_a["pin"] and addr_a["pin"] == addr_b["pin"]:
        score += 1
    if addr_a["city"] and addr_a["city"] == addr_b["city"]:
        score += 1

    status = "PASS" if score == 2 else "WARNING" if score == 1 else "FAIL"

    return {
        "rule": label,
        "status": status,
        "details": f"Address match score: {score}/2"
    }


def rule_incorporation_check(entity: Dict) -> Dict:
    inc = entity["udyam"].get("incorporation_date")
    com = entity["udyam"].get("commencement_date")

    status = "WARNING" if inc == com else "PASS"

    return {
        "rule": "INCORPORATION_VS_COMMENCEMENT",
        "status": status,
        "details": "Same date indicates possible existing entity"
    }


# ---------------------------
# Verification Orchestrator
# ---------------------------

def run_verification(entity: Dict) -> List[Dict]:
    results = []

    # Name consistency
    results.append(rule_name_match(entity, "pan", "gst"))
    results.append(rule_name_match(entity, "pan", "udyam"))
    results.append(rule_name_match(entity, "gst", "udyam"))

    # PAN consistency
    results.append(rule_pan_match(entity, "gst"))
    results.append(rule_pan_match(entity, "udyam"))

    # Address checks
    results.append(
        rule_address_match(
            entity["gst"]["principal_address"],
            entity["udyam"]["registered_address"],
            "GST_UDYAM_PRINCIPAL_ADDRESS_MATCH"
        )
    )

    # Incorporation logic
    results.append(rule_incorporation_check(entity))

    return results


# ---------------------------
# Main Runner
# ---------------------------

def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    pan_raw = load_json(r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\project\output\pan_output.json")
    gst_raw = load_json(r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\project\output\gst_output.json")
    udyam_raw = load_json(r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\project\output\udyam_output.json")

    pan = pan_adapter(pan_raw)
    gst = gst_adapter(gst_raw)
    udyam = udyam_adapter(udyam_raw)

    entity = build_entity(pan, gst, udyam)

    verification_results = run_verification(entity)

    print("\nVERIFICATION REPORT\n" + "-" * 40)
    for r in verification_results:
        print(f"{r['rule']} -> {r['status']} | {r['details']}")
