# import re
# from typing import Dict, List, Any
# def extract_udyam_fields(raw_text: str) -> dict:
#     raw = raw_text
#     text = raw_text.upper()

#     data = {
#         "document_type": "UDYAM",
#         "fields": {},
#         "tables": {},
#         "flags": [],
#         "missing_fields": []
#     }

#     # Udyam Number
#     m = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", text)
#     if m:
#         data["fields"]["udyam_number"] = m.group()
#     else:
#         data["missing_fields"].append("udyam_number")

#     # Enterprise Name (DO NOT NORMALIZE)
#     m = re.search(r"NAME OF ENTERPRISE\s*[:\-]?\s*(.+?)\n", raw, re.IGNORECASE)
#     if m:
#         data["fields"]["enterprise_name"] = m.group(1).strip()
#     else:
#         data["missing_fields"].append("enterprise_name")

#     # PAN
#     m = re.search(r"\b([A-Z]{5}\d{4}[A-Z])\b", text)
#     if m:
#         data["fields"]["pan"] = m.group(1)
#     else:
#         data["missing_fields"].append("pan")

#     # Dates
#     def extract_date(label):
#         m = re.search(rf"{label}.*?(\d{{2}}/\d{{2}}/\d{{4}})", text)
#         return m.group(1) if m else None

#     data["fields"]["incorporation_date"] = extract_date("DATE OF INCORPORATION")
#     data["fields"]["commencement_date"] = extract_date("DATE OF COMMENCEMENT")

#     # Date logic flag
#     if (data["fields"].get("incorporation_date") and
#         data["fields"].get("commencement_date") and
#         data["fields"]["incorporation_date"] == data["fields"]["commencement_date"]):
#         data["flags"].append({
#             "code": "INCORPORATION_EQUALS_COMMENCEMENT",
#             "severity": "HIGH"
#         })

#     # Address
#     data["fields"]["official_address"] = extract_official_address(text)

#     # Tables
#     data["tables"]["classification_history"] = extract_classification_table(text)
#     data["tables"]["employment_details"] = extract_employment_table(text)
#     data["tables"]["investment_details"] = extract_investment_table(text)
#     data["tables"]["units_details"] = extract_units_table(text)
#     data["tables"]["nic_codes"] = extract_nic_table(text)
#     data["tables"]["bank_details"] = extract_bank_details(text)

#     return data

# # def extract_udyam_fields(raw_text: str) -> dict:
# #     """
# #     Extract fields and tables from Udyam Registration Certificate
# #     """
# #     text = raw_text.upper()

# #     data = {
# #         "document_type": "UDYAM",
# #         "fields": {},
# #         "tables": {},
# #         "flags": []
# #     }

# #     # ============ BASIC FIELDS EXTRACTION ============

# #     # Udyam Number
# #     m = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d+", text)
# #     if m:
# #         data["fields"]["udyam_number"] = m.group()

# #     # Enterprise Name
# #     m = re.search(r"NAME OF ENTERPRISE\s+(.*?)\s+TYPE OF ENTERPRISE", text, re.S)
# #     if m:
# #         data["fields"]["enterprise_name"] = m.group(1).strip()

# #     # Enterprise Type (Micro/Small/Medium) - get current classification
# #     m = re.search(r"TYPE OF ENTERPRISE\s+\*?\s*(MICRO|SMALL|MEDIUM)", text)
# #     if m:
# #         data["fields"]["enterprise_type"] = m.group(1)

# #     # Major Activity
# #     if "MANUFACTURING" in text:
# #         data["fields"]["major_activity"] = "MANUFACTURING"
# #     elif "SERVICE" in text:
# #         data["fields"]["major_activity"] = "SERVICE"

# #     # Type of Organisation
# #     m = re.search(r"TYPE OF ORGANISATION\s+([A-Z\s]+?)(?:NAME OF ENTERPRISE|OWNER NAME)", text)
# #     if m:
# #         data["fields"]["organisation_type"] = m.group(1).strip()

# #     # PAN
# #     m = re.search(r"PAN\s+([A-Z]{5}\d{4}[A-Z])", text)
# #     if m:
# #         data["fields"]["pan"] = m.group(1)

# #     # GST Status
# #     if "DO YOU HAVE GSTIN YES" in text or re.search(r"DO YOU HAVE GSTIN\s+YES", text):
# #         data["fields"]["gst_available"] = True
# #     else:
# #         data["fields"]["gst_available"] = False

# #     # Mobile
# #     m = re.search(r"MOBILE(?:\s+NO\.?)?\s+(\d{10})", text)
# #     if m:
# #         data["fields"]["mobile"] = m.group(1)

# #     # Email
# #     m = re.search(r"EMAIL(?:\s+ID)?\s*:?\s+([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", text)
# #     if m:
# #         data["fields"]["email"] = m.group(1)

# #     # Social Category - Fixed pattern
# #     m = re.search(r"SOCIAL CATEGORY(?:\s+OF\s+ENTREPRENEUR)?\s+(GENERAL|SC|ST|OBC)", text)
# #     if m:
# #         data["fields"]["social_category"] = m.group(1)

# #     # Gender
# #     m = re.search(r"GENDER\s+(MALE|FEMALE|OTHER)", text)
# #     if m:
# #         data["fields"]["gender"] = m.group(1)

# #     # Incorporation Date
# #     m = re.search(r"DATE OF INCORPORATION.*?(\d{2}/\d{2}/\d{4})", text)
# #     if m:
# #         data["fields"]["incorporation_date"] = m.group(1)

# #     # Commencement/Production Date
# #     m = re.search(r"DATE OF COMMENCEMENT.*?(\d{2}/\d{2}/\d{4})", text)
# #     if m:
# #         data["fields"]["commencement_date"] = m.group(1)

# #     # Date of Udyam Registration
# #     m = re.search(r"DATE OF UDYAM REGISTRATION\s+(\d{2}/\d{2}/\d{4})", text)
# #     if m:
# #         data["fields"]["udyam_registration_date"] = m.group(1)

# #     # State - Fixed
# #     m = re.search(r"STATE\s+(GUJARAT|[A-Z]+(?:\s+[A-Z]+)?)\s+DISTRICT", text)
# #     if m:
# #         data["fields"]["state"] = m.group(1).strip()

# #     # District - Fixed
# #     m = re.search(r"DISTRICT\s+([A-Z]+(?:\s+[A-Z]+)?)\s*,?\s*(?:PIN|\d)", text)
# #     if m:
# #         data["fields"]["district"] = m.group(1).strip()

# #     # City - Fixed
# #     m = re.search(r"CITY\s+(AHMEDABAD|[A-Z]+(?:\s+[A-Z]+)?)\s+STATE", text)
# #     if m:
# #         data["fields"]["city"] = m.group(1).strip()

# #     # ============ OFFICIAL ADDRESS EXTRACTION ============
# #     data["fields"]["official_address"] = extract_official_address(text)

# #     # ============ TABLE EXTRACTIONS ============

# #     # Table 1: Enterprise Type Classification History
# #     data["tables"]["classification_history"] = extract_classification_table(text)

# #     # Table 2: Employment Details
# #     data["tables"]["employment_details"] = extract_employment_table(text)

# #     # Table 3: Investment in Plant & Machinery / Equipment
# #     data["tables"]["investment_details"] = extract_investment_table(text)

# #     # Table 4: Unit(s) Details
# #     data["tables"]["units_details"] = extract_units_table(text)

# #     # Table 5: NIC Code(s) Details
# #     data["tables"]["nic_codes"] = extract_nic_table(text)

# #     # Table 6: Bank Details
# #     data["tables"]["bank_details"] = extract_bank_details(text)


# #     # ============ VALIDATION FLAGS ============

# #     # Check if incorporation and commencement dates are same
# #     if (data["fields"].get("incorporation_date") == 
# #         data["fields"].get("commencement_date")):
# #         data["flags"].append("INCORPORATION_AND_COMMENCEMENT_DATE_SAME")

# #     return data


# def extract_official_address(text: str) -> Dict[str, str]:
#     """
#     Extract the complete Official Address of Enterprise
#     Based on the exact structure in the PDF
#     """
#     address = {}

#     # The official address appears twice - we want the FIRST occurrence
#     # Pattern: OFFICAL ADDRESS OF ENTERPRISE (typo in original PDF)
#     addr_match = re.search(
#         r"OFFIC[AI]AL ADDRESS OF ENTERPRISE(.*?)(?:DATE OF INCORPORATION|NATIONAL INDUSTRY)",
#         text,
#         re.S
#     )

#     if addr_match:
#         addr_text = addr_match.group(1)

#         # Flat/Door/Block No - Pattern: "FLAT/DOOR/BLOCK NO. B-26"
#         m = re.search(r"(?:FLAT/DOOR/BLOCK|FLAT)\s+(?:NO\.?|NUMBER)?\s+([A-Z0-9-]+)", addr_text)
#         if m:
#             address["flat_no"] = m.group(1).strip()

#         # Building - Pattern: "NAME OF PREMISES/ BUILDING Galaxy Signature"
#         m = re.search(r"NAME OF\s+PREMISES[/\s]+BUILDING\s+([A-Z][A-Z\s]+?)(?:VILLAGE|TOWN)", addr_text)
#         if m:
#             address["building"] = m.group(1).strip()

#         # Village/Town - Pattern: "VILLAGE/TOWN Sola"
#         m = re.search(r"VILLAGE/TOWN\s+([A-Z][A-Z\s]+?)(?:BLOCK|\s+BLOCK)", addr_text)
#         if m:
#             address["village_town"] = m.group(1).strip()

#         # Block - Pattern: "BLOCK Science City"
#         m = re.search(r"BLOCK\s+([A-Z][A-Z\s]+?)(?:ROAD|STREET)", addr_text)
#         if m:
#             address["block"] = m.group(1).strip()

#         # Road - Pattern: "ROAD/STREET/LANE Science City Road"
#         m = re.search(r"(?:ROAD/STREET/LANE|ROAD)\s+([A-Z][A-Z\s]+?)(?:CITY)", addr_text)
#         if m:
#             address["road"] = m.group(1).strip()

#         # City - Pattern: "CITY Ahmedabad"
#         m = re.search(r"CITY\s+([A-Z][A-Z]+)\s+STATE", addr_text)
#         if m:
#             address["city"] = m.group(1).strip()

#         # State - Pattern: "STATE GUJARAT"
#         m = re.search(r"STATE\s+(GUJARAT|[A-Z]+(?:\s+[A-Z]+)?)\s+DISTRICT", addr_text)
#         if m:
#             address["state"] = m.group(1).strip()

#         # District - Pattern: "DISTRICT AHMADABAD , Pin 380060"
#         m = re.search(r"DISTRICT\s+([A-Z]+(?:\s+[A-Z]+)?)\s*,?\s*(?:PIN|Pin)\s*:?\s*(\d{6})", addr_text)
#         if m:
#             address["district"] = m.group(1).strip()
#             address["pin"] = m.group(2).strip()

#         # Mobile - Pattern: "MOBILE 9328255422"
#         m = re.search(r"MOBILE\s+(\d{10})", addr_text)
#         if m:
#             address["mobile"] = m.group(1)

#         # Email - Pattern: "EMAIL: stellinoxstainless@gmail.com"
#         m = re.search(r"EMAIL\s*:?\s+([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", addr_text)
#         if m:
#             address["email"] = m.group(1)

#     return address


# def extract_classification_table(text: str) -> List[Dict[str, str]]:
#     """
#     Extract Enterprise Type Classification History table
#     """
#     table_data = []
#     pattern = r"(\d+)\s+(\d{4}-\d{2})\s+(MICRO|SMALL|MEDIUM)\s+(\d{2}/\d{2}/\d{4})"

#     matches = re.finditer(pattern, text)
#     for match in matches:
#         table_data.append({
#             "sno": match.group(1),
#             "classification_year": match.group(2),
#             "enterprise_type": match.group(3),
#             "classification_date": match.group(4)
#         })

#     return table_data


# def extract_employment_table(text: str) -> Dict[str, Any]:
#     """
#     Extract Employment Details
#     Pattern in PDF: "EMPLOYMENT DETAILS Male Female Other Total 40 0 0 40"
#     """
#     employment = {}

#     # Pattern: EMPLOYMENT DETAILS followed by Male Female Other Total and then 4 numbers
#     m = re.search(r"EMPLOYMENT DETAILS\s+MALE\s+FEMALE\s+OTHER\s+TOTAL\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text)
#     if m:
#         employment = {
#             "male": int(m.group(1)),
#             "female": int(m.group(2)),
#             "other": int(m.group(3)),
#             "total": int(m.group(4))
#         }

#     return employment


# def extract_investment_table(text: str) -> List[Dict[str, Any]]:
#     """
#     Extract Investment in Plant and Machinery OR Equipment table
#     Pattern in PDF has columns with financial data
#     """
#     table_data = []

#     # More flexible pattern that captures the investment table rows
#     # Pattern: S.No Year Type WDV Exclusion NetInv TotalTurnover ExportTurnover NetTurnover ITRFilled ITRType
#     pattern = r"(\d+)\s+(\d{4}-\d{2})\s+(MICRO|SMALL|MEDIUM)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(YES|NO)\s+ITR\s*-?\s*([\d,\s]+)"

#     matches = re.finditer(pattern, text)
#     for match in matches:
#         table_data.append({
#             "sno": match.group(1),
#             "financial_year": match.group(2),
#             "enterprise_type": match.group(3),
#             "wdv": float(match.group(4)),
#             "exclusion_cost": float(match.group(5)),
#             "net_investment": float(match.group(6)),
#             "total_turnover": float(match.group(7)),
#             "export_turnover": float(match.group(8)),
#             "net_turnover": float(match.group(9)),
#             "itr_filled": match.group(10) == "YES",
#             "itr_type": match.group(11).strip()
#         })

#     return table_data


# def extract_units_table(text: str) -> List[Dict[str, str]]:
#     """
#     Extract Unit(s) Details table
#     Pattern: Unit Name followed by address components in table format
#     """
#     table_data = []

#     # Find the Unit(s) Details section
#     unit_section = re.search(r"UNIT\(S\) DETAILS(.*?)OFFICIAL ADDRESS OF ENTERPRISE", text, re.S)
#     if unit_section:
#         unit_text = unit_section.group(1)

#         # Pattern for the table row: "1 M/S STELLINOX... Survey No: 33,34 &35 Jasalpur..."
#         # Extract unit number, name, and full address
#         pattern = r"(\d+)\s+(M/S\s+[A-Z\s]+?)\s+(SURVEY NO:|FLAT|PLOT)\s*:?\s*([\d,\s&A-Z]+)\s+([A-Z][A-Z\s]+?)\s+([A-Z][A-Z\s]+?)\s+([A-Z][A-Z]+)\s+([A-Z][A-Z\s]+?)\s+(\d{6})\s+(GUJARAT|[A-Z]+)\s+([A-Z]+)"

#         matches = re.finditer(pattern, unit_text)
#         for match in matches:
#             table_data.append({
#                 "sno": match.group(1),
#                 "unit_name": match.group(2).strip(),
#                 "flat": match.group(4).strip(),
#                 "building": match.group(5).strip(),
#                 "village_town": match.group(6).strip(),
#                 "block": match.group(7).strip(),
#                 "road": match.group(8).strip(),
#                 "pin": match.group(9),
#                 "state": match.group(10).strip(),
#                 "district": match.group(11).strip()
#             })

#     return table_data


# def extract_nic_table(text: str) -> List[Dict[str, str]]:
#     """
#     Extract National Industry Classification Code(S) table
#     Pattern in PDF: "1 24 - Manufacture of basic metals 2410 - Manufacture of basic iron and steel..."
#     """
#     table_data = []

#     # Pattern: SNo NIC2Digit-Description NIC4Digit-Description NIC5Digit-Description Activity
#     pattern = r"(\d+)\s+(\d{2})\s*-\s*([A-Z][^\d]+?)\s+(\d{4})\s*-\s*([A-Z][^\d]+?)\s+(\d{5})\s*-\s*([^\n]+?)\s+(MANUFACTURING|SERVICE)"

#     matches = re.finditer(pattern, text)
#     seen_codes = set()  # To avoid duplicates

#     for match in matches:
#         nic_5_digit = match.group(6)
#         if nic_5_digit not in seen_codes:
#             seen_codes.add(nic_5_digit)
#             table_data.append({
#                 "sno": match.group(1),
#                 "nic_2_digit": f"{match.group(2)} - {match.group(3).strip()}",
#                 "nic_4_digit": f"{match.group(4)} - {match.group(5).strip()}",
#                 "nic_5_digit": f"{match.group(6)} - {match.group(7).strip()}",
#                 "activity": match.group(8)
#             })

#     return table_data


# def extract_bank_details(text: str) -> Dict[str, str]:
#     """
#     Extract Bank Details
#     Pattern in PDF:
#     Bank Details
#     Bank Name       IFS Code        Bank Account Number
#     icici bank limited   ICIC0007713     771305000097
#     """
#     bank_details = {}

#     # Find the Bank Details section - it appears on page 2
#     # Pattern: BANK DETAILS followed by headers then data
#     bank_section = re.search(
#         r"BANK DETAILS\s+BANK NAME\s+IFS CODE\s+BANK ACCOUNT NUMBER\s+([A-Z][A-Z\s&.]+?)\s+([A-Z]{4}0[A-Z0-9]{6})\s+(\d+)",
#         text
#     )

#     if bank_section:
#         bank_details["bank_name"] = bank_section.group(1).strip()
#         bank_details["ifsc_code"] = bank_section.group(2).strip()
#         bank_details["account_number"] = bank_section.group(3).strip()

#     return bank_details


import re
import json
from typing import Dict, List, Any


def extract_udyam_fields(raw_text: str) -> dict:
    """
    Extract fields and tables from Udyam Registration Certificate.
    Returns structured JSON with all extracted data.
    """
    raw = raw_text
    text = raw_text.upper()
    
    data = {
        "document_type": "UDYAM",
        "fields": {},
        "tables": {},
        "flags": [],
        "missing_fields": []
    }
    
    # ============ BASIC FIELDS EXTRACTION ============
    
    # Udyam Number
    m = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", text)
    if m:
        data["fields"]["udyam_number"] = m.group()
    else:
        data["missing_fields"].append("udyam_number")
    
    # Enterprise Name (DO NOT NORMALIZE)
    m = re.search(r"NAME OF ENTERPRISE\s*[:\-]?\s*(.+?)\n", raw, re.IGNORECASE)
    if m:
        data["fields"]["enterprise_name"] = m.group(1).strip()
    else:
        data["missing_fields"].append("enterprise_name")
    
    # PAN
    m = re.search(r"\b([A-Z]{5}\d{4}[A-Z])\b", text)
    if m:
        data["fields"]["pan"] = m.group(1)
    else:
        data["missing_fields"].append("pan")
    
    # Mobile
    m = re.search(r"MOBILE\s+(\d{10})", text)
    if m:
        data["fields"]["mobile"] = m.group(1)
    
    # Email
    m = re.search(r"EMAIL\s*:?\s+([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", text)
    if m:
        data["fields"]["email"] = m.group(1)
    
    # Dates
    def extract_date(label):
        m = re.search(rf"{label}.*?(\d{{2}}/\d{{2}}/\d{{4}})", text)
        return m.group(1) if m else None
    
    data["fields"]["incorporation_date"] = extract_date("DATE OF INCORPORATION")
    data["fields"]["commencement_date"] = extract_date("DATE OF COMMENCEMENT")
    
    # Date logic flag
    if (data["fields"].get("incorporation_date") and 
        data["fields"].get("commencement_date") and
        data["fields"]["incorporation_date"] == data["fields"]["commencement_date"]):
        data["flags"].append({
            "code": "INCORPORATION_EQUALS_COMMENCEMENT",
            "severity": "HIGH"
        })
    
    # Address
    data["fields"]["official_address"] = extract_official_address(text)
    
    # ============ TABLE EXTRACTIONS ============
    data["tables"]["classification_history"] = extract_classification_table(text)
    data["tables"]["employment_details"] = extract_employment_table(text)
    data["tables"]["investment_details"] = extract_investment_table(text)
    data["tables"]["units_details"] = extract_units_table(text)
    data["tables"]["nic_codes"] = extract_nic_table(text)
    data["tables"]["bank_details"] = extract_bank_details(text)
    
    return data


def extract_official_address(text: str) -> Dict[str, str]:
    """Extract the complete Official Address of Enterprise."""
    address = {}
    
    addr_match = re.search(
        r"OFFIC[AI]AL ADDRESS OF ENTERPRISE(.*?)(?:DATE OF INCORPORATION|NATIONAL INDUSTRY)",
        text,
        re.S
    )
    
    if addr_match:
        addr_text = addr_match.group(1)
        
        # Flat/Door/Block No
        m = re.search(r"(?:FLAT/DOOR/BLOCK|FLAT)\s+(?:NO\.?|NUMBER)?\s+([A-Z0-9-]+)", addr_text)
        if m:
            address["flat_no"] = m.group(1).strip()
        
        # Building
        m = re.search(r"NAME OF\s+PREMISES[/\s]+BUILDING\s+([A-Z][A-Z\s]+?)(?:VILLAGE|TOWN)", addr_text)
        if m:
            address["building"] = m.group(1).strip()
        
        # Village/Town
        m = re.search(r"VILLAGE/TOWN\s+([A-Z][A-Z\s]+?)(?:BLOCK|\s+BLOCK)", addr_text)
        if m:
            address["village_town"] = m.group(1).strip()
        
        # Block
        m = re.search(r"BLOCK\s+([A-Z][A-Z\s]+?)(?:ROAD|STREET)", addr_text)
        if m:
            address["block"] = m.group(1).strip()
        
        # Road
        m = re.search(r"(?:ROAD/STREET/LANE|ROAD)\s+([A-Z][A-Z\s]+?)(?:CITY)", addr_text)
        if m:
            address["road"] = m.group(1).strip()
        
        # City
        m = re.search(r"CITY\s+([A-Z][A-Z]+)\s+STATE", addr_text)
        if m:
            address["city"] = m.group(1).strip()
        
        # State
        m = re.search(r"STATE\s+(GUJARAT|[A-Z]+(?:\s+[A-Z]+)?)\s+DISTRICT", addr_text)
        if m:
            address["state"] = m.group(1).strip()
        
        # District & Pin
        m = re.search(r"DISTRICT\s+([A-Z]+(?:\s+[A-Z]+)?)\s*,?\s*(?:PIN|Pin)\s*:?\s*(\d{6})", addr_text)
        if m:
            address["district"] = m.group(1).strip()
            address["pin"] = m.group(2).strip()
        
        # Mobile
        m = re.search(r"MOBILE\s+(\d{10})", addr_text)
        if m:
            address["mobile"] = m.group(1)
        
        # Email
        m = re.search(r"EMAIL\s*:?\s+([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", addr_text)
        if m:
            address["email"] = m.group(1)
    
    return address


def extract_classification_table(text: str) -> List[Dict[str, str]]:
    """Extract Enterprise Type Classification History table."""
    table_data = []
    pattern = r"(\d+)\s+(\d{4}-\d{2})\s+(MICRO|SMALL|MEDIUM)\s+(\d{2}/\d{2}/\d{4})"
    
    matches = re.finditer(pattern, text)
    for match in matches:
        table_data.append({
            "sno": match.group(1),
            "classification_year": match.group(2),
            "enterprise_type": match.group(3),
            "classification_date": match.group(4)
        })
    
    return table_data


def extract_employment_table(text: str) -> Dict[str, Any]:
    """Extract Employment Details."""
    employment = {}
    m = re.search(r"EMPLOYMENT DETAILS\s+MALE\s+FEMALE\s+OTHER\s+TOTAL\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text)
    
    if m:
        employment = {
            "male": int(m.group(1)),
            "female": int(m.group(2)),
            "other": int(m.group(3)),
            "total": int(m.group(4))
        }
    
    return employment


def extract_investment_table(text: str) -> List[Dict[str, Any]]:
    """Extract Investment in Plant and Machinery OR Equipment table."""
    table_data = []
    pattern = r"(\d+)\s+(\d{4}-\d{2})\s+(MICRO|SMALL|MEDIUM)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(YES|NO)\s+ITR\s*-?\s*([\d,\s]+)"
    
    matches = re.finditer(pattern, text)
    for match in matches:
        table_data.append({
            "sno": match.group(1),
            "financial_year": match.group(2),
            "enterprise_type": match.group(3),
            "wdv": float(match.group(4)),
            "exclusion_cost": float(match.group(5)),
            "net_investment": float(match.group(6)),
            "total_turnover": float(match.group(7)),
            "export_turnover": float(match.group(8)),
            "net_turnover": float(match.group(9)),
            "itr_filled": match.group(10) == "YES",
            "itr_type": match.group(11).strip()
        })
    
    return table_data


def extract_units_table(text: str) -> List[Dict[str, str]]:
    """Extract Unit(s) Details table."""
    table_data = []
    unit_section = re.search(r"UNIT\(S\) DETAILS(.*?)OFFICIAL ADDRESS OF ENTERPRISE", text, re.S)
    
    if unit_section:
        unit_text = unit_section.group(1)
        pattern = r"(\d+)\s+(M/S\s+[A-Z\s]+?)\s+(SURVEY NO:|FLAT|PLOT)\s*:?\s*([\d,\s&A-Z]+)\s+([A-Z][A-Z\s]+?)\s+([A-Z][A-Z\s]+?)\s+([A-Z][A-Z]+)\s+([A-Z][A-Z\s]+?)\s+(\d{6})\s+(GUJARAT|[A-Z]+)\s+([A-Z]+)"
        
        matches = re.finditer(pattern, unit_text)
        for match in matches:
            table_data.append({
                "sno": match.group(1),
                "unit_name": match.group(2).strip(),
                "flat": match.group(4).strip(),
                "building": match.group(5).strip(),
                "village_town": match.group(6).strip(),
                "block": match.group(7).strip(),
                "road": match.group(8).strip(),
                "pin": match.group(9),
                "state": match.group(10).strip(),
                "district": match.group(11).strip()
            })
    
    return table_data


def extract_nic_table(text: str) -> List[Dict[str, str]]:
    """Extract National Industry Classification Code(S) table."""
    table_data = []
    pattern = r"(\d+)\s+(\d{2})\s*-\s*([A-Z][^\d]+?)\s+(\d{4})\s*-\s*([A-Z][^\d]+?)\s+(\d{5})\s*-\s*([^\n]+?)\s+(MANUFACTURING|SERVICE)"
    
    matches = re.finditer(pattern, text)
    seen_codes = set()
    
    for match in matches:
        nic_5_digit = match.group(6)
        if nic_5_digit not in seen_codes:
            seen_codes.add(nic_5_digit)
            table_data.append({
                "sno": match.group(1),
                "nic_2_digit": f"{match.group(2)} - {match.group(3).strip()}",
                "nic_4_digit": f"{match.group(4)} - {match.group(5).strip()}",
                "nic_5_digit": f"{match.group(6)} - {match.group(7).strip()}",
                "activity": match.group(8)
            })
    
    return table_data


def extract_bank_details(text: str) -> Dict[str, str]:
    """Extract Bank Details."""
    bank_details = {}
    bank_section = re.search(
        r"BANK DETAILS\s+BANK NAME\s+IFS CODE\s+BANK ACCOUNT NUMBER\s+([A-Z][A-Z\s&.]+?)\s+([A-Z]{4}0[A-Z0-9]{6})\s+(\d+)",
        text
    )
    
    if bank_section:
        bank_details["bank_name"] = bank_section.group(1).strip()
        bank_details["ifsc_code"] = bank_section.group(2).strip()
        bank_details["account_number"] = bank_section.group(3).strip()
    
    return bank_details


def print_udyam_results(result: dict):
    """Pretty print Udyam extraction results (optional utility function)."""
    print("\n" + "="*80)
    print("📋 UDYAM CERTIFICATE EXTRACTION RESULTS")
    print("="*80)
    
    print("\n📌 BASIC FIELDS:")
    print("-"*80)
    for key, value in result["fields"].items():
        if key != "official_address":
            print(f"   {key:30s}: {value}")
    
    print("\n🏢 OFFICIAL ADDRESS:")
    print("-"*80)
    addr = result["fields"].get("official_address", {})
    for key, value in addr.items():
        print(f"   {key:20s}: {value}")
    
    print("\n📊 TABLES:")
    print("="*80)
    
    if result["tables"]["classification_history"]:
        print("\n1️⃣  CLASSIFICATION HISTORY:")
        for rec in result["tables"]["classification_history"]:
            print(f"   {rec['classification_year']} | {rec['enterprise_type']} | {rec['classification_date']}")
    
    if result["tables"]["employment_details"]:
        print("\n2️⃣  EMPLOYMENT:")
        emp = result["tables"]["employment_details"]
        print(f"   Male: {emp['male']} | Female: {emp['female']} | Other: {emp['other']} | Total: {emp['total']}")
    
    if result["flags"]:
        print("\n⚠️  FLAGS:")
        for flag in result["flags"]:
            print(f"   🚩 {flag['code']} (Severity: {flag['severity']})")
