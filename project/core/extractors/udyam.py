import re

def extract_udyam_fields(raw_text: str) -> dict:
    text = raw_text.upper()

    data = {
        "document_type": "UDYAM",
        "fields": {},
        "flags": []
    }

    # Udyam Number
    m = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d+", text)
    if m:
        data["fields"]["udyam_number"] = m.group()

    # Enterprise Name
    m = re.search(r"NAME OF ENTERPRISE\s+(.*?)\s+TYPE OF ENTERPRISE", text, re.S)
    if m:
        data["fields"]["enterprise_name"] = m.group(1).strip()

    # Enterprise Type (Micro/Small/Medium)
    m = re.search(r"TYPE OF ENTERPRISE\s+\*?\s*(MICRO|SMALL|MEDIUM)", text)
    if m:
        data["fields"]["enterprise_type"] = m.group(1)
 
    # Major Activity
    if "MANUFACTURING" in text:
        data["fields"]["major_activity"] = "MANUFACTURING"

    # Incorporation Date
    m = re.search(r"DATE OF INCORPORATION.*?(\d{2}/\d{2}/\d{4})", text)
    if m:
        data["fields"]["incorporation_date"] = m.group(1)

    # Production Date
    m = re.search(r"DATE OF COMMENCEMENT.*?(\d{2}/\d{2}/\d{4})", text)
    if m:
        data["fields"]["production_date"] = m.group(1)

    # GST Exists
    if "DO YOU HAVE GSTIN YES" in text:
        data["fields"]["gst_available"] = True

    # State (via GST code or address)
    if " GUJARAT" in text:
        data["fields"]["state"] = "GUJARAT"

    # Logical flags
    if (
        data["fields"].get("incorporation_date")
        == data["fields"].get("production_date")
    ):
        data["flags"].append("INCORPORATION_AND_PRODUCTION_DATE_SAME")

    return data
