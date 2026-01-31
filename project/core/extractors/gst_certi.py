import re
from typing import Dict, List, Optional, Tuple, Any, Union


def _post_process_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final validation / cleaning pass on all extracted fields,
    plus sub-field structuring for principal_address.
    """
    out = dict(fields)

    # name cleanup
    if out.get("name"):
        out["name"] = _clean_field_value(out["name"])

    # constitution normalization
    if out.get("constitution_of_business"):
        out["constitution_of_business"] = _normalize_constitution(out["constitution_of_business"])

    # principal address → structured dictionary
    if out.get("principal_address"):
        if isinstance(out["principal_address"], str):
            structured = _structure_principal_address(out["principal_address"])
            if structured:
                out["principal_address"] = structured
            else:
                # Return empty dict if can't structure
                out["principal_address"] = {}
        # If already a dict, keep it

    # approving authority cleanup
    if out.get("particulars_of_approving_authority"):
        out["particulars_of_approving_authority"] = _clean_field_value(
            out["particulars_of_approving_authority"]
        )

    # gst number validation
    if out.get("gst_number"):
        out["gst_number"] = _validate_gstin(out["gst_number"])

    # total_no_of_additional_places normalization
    total = out.get("total_no_of_additional_places") or ""
    if isinstance(total, str) and total.isdigit():
        out["total_no_of_additional_places"] = str(int(total))  # remove leading zeros
    else:
        out["total_no_of_additional_places"] = ""

    # additional_place_of_business consistency
    if out["total_no_of_additional_places"] == "0":
        out["additional_place_of_business"] = "NA"
    elif not out["total_no_of_additional_places"]:
        out["additional_place_of_business"] = ""

    return out

def _merge_fragmented_ocr_lines(text: str) -> str:
    """
    Merge fragmented OCR lines where labels are split across multiple lines.
    Handles heavily fragmented patterns like:
        "Floor" + "No.:" + "9TH" → "Floor No.: 9TH"
        "Building" + "No./Flat" + "No.:" + "903-918" → "Building No./Flat No.: 903-918"
    """
    lines = text.split('\n')
    merged_lines = []
    i = 0
    
    # Label keywords that start a field definition
    LABEL_STARTS = {'floor', 'building', 'name', 'road', 'nearby', 'locality', 
                    'city', 'district', 'state', 'pin'}
    # Parts that continue a label
    LABEL_PARTS = {'no', 'no.', 'no.:', 'no:', '/', 'flat', 'of', 'premises', 
                   'street', 'landmark', 'sub', 'town', 'village', 'code', 
                   'cod', 'local', '/sub', '/street', '/flat', '/town', '/building'}
    
    while i < len(lines):
        line = lines[i].strip()
        line_lower = line.lower().rstrip(':')
        
        # Check if this line starts a label
        if line_lower in LABEL_STARTS or line_lower.rstrip(':') in LABEL_STARTS:
            # Collect the full label and value
            merged = line
            j = i + 1
            found_value = False
            
            while j < len(lines) and j < i + 8:  # Look ahead max 7 lines
                next_line = lines[j].strip()
                next_lower = next_line.lower().rstrip(':')
                
                # Stop if we hit another label start (new field)
                if next_lower in LABEL_STARTS and ':' not in merged:
                    break
                
                # Check if this is a label part
                if next_lower in LABEL_PARTS or next_lower.replace('.', '') in LABEL_PARTS:
                    merged += ' ' + next_line
                    j += 1
                elif ':' in next_line and not found_value:
                    # This contains the colon delimiter
                    merged += ' ' + next_line
                    j += 1
                    # If colon is at the end, value is on next line
                    if merged.rstrip().endswith(':') and j < len(lines):
                        value_line = lines[j].strip()
                        if value_line and value_line.lower().rstrip(':') not in LABEL_STARTS:
                            merged += ' ' + value_line
                            j += 1
                            found_value = True
                elif not found_value and not next_lower in LABEL_STARTS:
                    # This is likely the value
                    merged += ' ' + next_line
                    j += 1
                    found_value = True
                else:
                    break
            
            merged_lines.append(merged)
            i = j
        else:
            merged_lines.append(line)
            i += 1
    
    return '\n'.join(merged_lines)


def _extract_labeled_address_fields(address: str) -> Dict[str, str]:
    """
    Extract address fields from pre-labeled text lines like:
        "Building No./Flat No.: D-1"
        "Name of Premises/Building: KONCEM TOWER"
        "Floor No.: 9TH Building No./Flat No.: 903-918"
    
    Returns a dictionary with extracted fields.
    """
    result: Dict[str, str] = {}
    
    # Merge fragmented OCR lines first
    address = _merge_fragmented_ocr_lines(address)
    
    # Process the address text - normalize whitespace
    addr_for_matching = re.sub(r'[ \t]+', ' ', address)
    addr_for_matching = re.sub(r'\n+', ' ', addr_for_matching)  # Convert newlines to spaces for matching
    
    # Label patterns to match - ordered by specificity (more specific first)
    # Each pattern captures the value after the label
    label_patterns = [
        # Floor number
        (r"floor\s*(?:no\.?)?\s*:\s*(\S+)", "floor_no"),
        # Building/Flat number - handle both formats
        (r"(?:building|bldg)\s*(?:no\.?)?\s*/?\s*(?:flat)?\s*(?:no\.?)?\s*:\s*([^,\n]+?)(?=\s+(?:name|road|nearby|locality|city|district|state|pin|floor|\d+\.|$))", "building_flat_no"),
        (r"flat\s*(?:no\.?)?\s*:\s*([^,\n]+?)(?=\s+(?:name|road|nearby|locality|city|district|state|pin|building|\d+\.|$))", "building_flat_no"),
        # Name of premises/building
        (r"name\s*(?:of)?\s*premises\s*/?\s*(?:building)?\s*:\s*([^,\n]+?)(?=\s+(?:road|nearby|locality|city|district|state|pin|\d+\.|$))", "premises_name"),
        # Road/Street
        (r"road\s*/?\s*(?:street)?\s*:\s*([^,\n]+?)(?=\s+(?:nearby|landmark|locality|city|district|state|pin|\d+\.|$))", "road_street"),
        # Nearby Landmark
        (r"(?:nearby)?\s*landmark\s*:\s*([^,\n]+?)(?=\s+(?:locality|city|district|state|pin|\d+\.|$))", "nearby_landmark"),
        # Locality/Sub Locality - handle truncated like "Local"
        (r"locality\s*/?\s*(?:sub)?\s*(?:local)?\s*[ity]*\s*:\s*([^,\n]+?)(?=\s+(?:city|district|state|pin|\d+\.|$))", "locality"),
        # City/Town/Village - handle truncated forms
        (r"city\s*/?\s*(?:town)?\s*/?\s*(?:vi(?:llage)?)?[a-z]*\s*:\s*([^,\n]+?)(?=\s+(?:district|state|pin|\d+\.|$))", "city"),
        # District
        (r"district\s*:\s*([^,\n]+?)(?=\s+(?:state|pin|\d+\.|$))", "district"),
        # State
        (r"state\s*:\s*([^,\n]+?)(?=\s+(?:pin|\d+\.|$))", "state"),
        # PIN Code - may be truncated like "880015" 
        (r"pin\s*(?:code?)?\s*(?:cod)?\s*:\s*(\d{5,6})", "pin_code"),
    ]
    
    for pattern, field_key in label_patterns:
        if field_key in result:  # Skip if already found
            continue
        match = re.search(pattern, addr_for_matching, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Clean the value - remove trailing commas, colons and extra whitespace
            value = re.sub(r'[\s,:]+$', '', value)
            value = re.sub(r'\s+', ' ', value)
            # Remove any embedded label fragments from value
            value = re.sub(r'\b(Business|No\.|no\.|No:|no:)\b', '', value, flags=re.IGNORECASE)
            value = value.strip()
            
            # Apply OCR corrections for common watermark-affected misreads
            ocr_fixes = {
                "viarat": "Gujarat",
                "ujarat": "Gujarat",
                "Gujrat": "Gujarat",
                "edabad": "Ahmedabad",
                "Ahn Laba": "Ahmedabad",
                "Ahm Laba": "Ahmedabad",
                "aria Restaurant": "Aria Restaurant",  # Common landmark
            }
            for bad, good in ocr_fixes.items():
                if bad.lower() in value.lower():
                    value = re.sub(re.escape(bad), good, value, flags=re.IGNORECASE)
            
            if value and len(value) > 0:
                result[field_key] = value
    
    return result


def _structure_principal_address(address: str) -> Dict[str, str]:
    """
    Build a structured principal_address dictionary with sub-fields:
    building_flat_no, premises_name, road_street, nearby_landmark,
    locality, city, district, state, pin_code.
    
    Uses label-first extraction if address contains labeled fields,
    otherwise falls back to token-based heuristics.
    
    Returns a dictionary with only non-empty fields.
    """
    raw = address
    addr = re.sub(r'\s+', ' ', raw).strip()
    
    # Check if address contains labeled fields (has ":" followed by values)
    # This indicates pre-labeled format like "Building No./Flat No.: D-1"
    has_labeled_fields = bool(re.search(
        r'(?:building|flat|floor|premises|road|street|landmark|locality|city|town|district|state|pin)\s*(?:no\.?|of|/)?\s*[^:]*:\s*\S+',
        addr,
        re.IGNORECASE
    ))
    
    if has_labeled_fields:
        # Use label-first extraction for pre-labeled addresses
        result = _extract_labeled_address_fields(raw)
        
        # Still need to extract PIN and state if not found via labels
        if "pin_code" not in result:
            m_pin = re.search(r'\b(\d{6})\b', addr)
            if m_pin:
                result["pin_code"] = m_pin.group(1)
        
        if "state" not in result:
            state_pattern = r'\b(gujarat|maharashtra|karnataka|tamil\s*nadu|telangana|andhra\s*pradesh|kerala|rajasthan|bihar|uttar\s*pradesh|madhya\s*pradesh|punjab|haryana|odisha|orissa|assam|jharkhand|chhattisgarh|goa|himachal\s*pradesh|uttarakhand|uttaranchal|west\s*bengal|delhi|jammu\s*(?:and|&)?\s*kashmir|ladakh|chandigarh|puducherry|pondicherry|sikkim|tripura|meghalaya|manipur|mizoram|arunachal\s*pradesh|nagaland)\b'
            m_state = re.search(state_pattern, addr.lower(), re.IGNORECASE)
            if m_state:
                result["state"] = m_state.group(1).strip().title()
        
        if result:  # Only return if we extracted something
            return result
    
    # Fall back to token-based extraction for comma-separated addresses
    # Remove any embedded GST form field labels that came from OCR
    field_labels = [
        r'Building\s*(?:No\.?|Number)\s*/?\s*Flat\s*(?:No\.?|Number)\s*:?',
        r'Name\s*(?:Of|of)\s*Premises\s*/?\s*Building\s*:?',
        r'Road\s*/?\s*Street\s*:?',
        r'Nearby\s*Landmark\s*:?',
        r'Locality\s*/?\s*Sub\s*Locality\s*:?',
        r'City\s*/?\s*Town\s*/?\s*Village\s*:?',
        r'District\s*:?',
        r'State\s*:?',
        r'PIN\s*(?:Code)?\s*:?',
        r'Floor\s*(?:No\.?)?\s*:?',
        r'Business\s*$',  # Remove trailing "Business" from split lines
    ]
    for label_pattern in field_labels:
        addr = re.sub(label_pattern, '', addr, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and commas
    addr = re.sub(r'\s+', ' ', addr)
    addr = re.sub(r',\s*,+', ',', addr)
    addr = re.sub(r'^\s*,\s*|\s*,\s*$', '', addr)
    addr = addr.strip()

    # OCR fixes for common misreads (especially watermark-affected)
    ocr_replacements = {
        # Ahmedabad variations
        "Ahn Laba": "Ahmedabad",
        "Ahm Laba": "Ahmedabad",
        "edabad": "Ahmedabad",  # Truncated version
        # Gujarat variations  
        "viarat": "Gujarat",
        "Gujrat": "Gujarat",
        "ujarat": "Gujarat",  # Truncated version
        # Other states
        "Maharastra": "Maharashtra",
        "Banglore": "Bangalore",
        "Bangaluru": "Bengaluru",
    }
    for bad, good in ocr_replacements.items():
        addr = re.sub(re.escape(bad), good, addr, flags=re.IGNORECASE)

    addr_lower = addr.lower()

    # Result dictionary
    result: Dict[str, str] = {}

    # Extract PIN Code (6 digits)
    m_pin = re.search(r'\b(\d{6})\b', addr)
    if m_pin:
        result["pin_code"] = m_pin.group(1)

    # Extract State
    state_pattern = r'\b(gujarat|maharashtra|karnataka|tamil\s*nadu|telangana|andhra\s*pradesh|kerala|rajasthan|bihar|uttar\s*pradesh|madhya\s*pradesh|punjab|haryana|odisha|orissa|assam|jharkhand|chhattisgarh|goa|himachal\s*pradesh|uttarakhand|uttaranchal|west\s*bengal|delhi|jammu\s*(?:and|&)?\s*kashmir|ladakh|chandigarh|puducherry|pondicherry|sikkim|tripura|meghalaya|manipur|mizoram|arunachal\s*pradesh|nagaland)\b'
    m_state = re.search(state_pattern, addr_lower, re.IGNORECASE)
    if m_state:
        result["state"] = m_state.group(1).strip().title()

    # Extract City / District
    city_pattern = r'\b(ahmedabad|mumbai|pune|bengaluru|bangalore|chennai|kolkata|delhi|surat|vadodara|jaipur|hyderabad|lucknow|kanpur|nagpur|indore|thane|bhopal|visakhapatnam|patna|ludhiana|agra|nashik|faridabad|meerut|rajkot|varanasi|srinagar|aurangabad|dhanbad|amritsar|ranchi|gwalior|coimbatore|vijayawada|jodhpur|madurai|raipur|kota|guwahati|chandigarh|solapur|hubli|mysore|tiruchirappalli|bareilly|aligarh|tiruppur|moradabad|jalandhar|bhubaneswar|salem|warangal|guntur|bhilai|cuttack|bikaner|amravati|noida|gurgaon|gandhinagar|mehsana|kadi)\b'
    m_city = re.search(city_pattern, addr_lower, re.IGNORECASE)
    if m_city:
        result["city"] = m_city.group(1).title()
        result["district"] = result["city"]

    # Tokenize by comma
    tokens = [t.strip() for t in addr.split(',') if t.strip()]
    used_indices = set()
    
    building_flat = ""
    premises_name = ""
    road_street = ""
    nearby = ""
    locality = ""

    if tokens:
        # Look for building/flat identifier patterns
        for i, t in enumerate(tokens):
            if i in used_indices:
                continue
            # Match F.P. NO-96, T.P. NO-408, Plot No. 5, B-26, etc.
            if re.search(r'(?:f\.?p\.?|t\.?p\.?|plot|flat|floor|shop|unit|office|block)\s*(?:no\.?)?\s*[-:]?\s*\d+', t, re.IGNORECASE):
                if not building_flat:
                    building_flat = t
                    used_indices.add(i)
            elif re.match(r'^[A-Z]-\d+', t.strip()):
                if not building_flat:
                    building_flat = t
                    used_indices.add(i)

        # Premises name: token with typical building words
        for i, t in enumerate(tokens):
            if i in used_indices:
                continue
            if re.search(r'\b(building|complex|solitaire|tower|arcade|center|centre|plaza|heights|residency|apartment|society|estate|park|house|galaxy|signature|business)\b', t, re.IGNORECASE):
                premises_name = t
                used_indices.add(i)
                break

        # Road/street
        for i, t in enumerate(tokens):
            if i in used_indices:
                continue
            if re.search(r'\b(road|rd\.?|street|st\.?|lane|marg|path|highway|avenue|chowk)\b', t, re.IGNORECASE):
                road_street = t
                used_indices.add(i)
                break

        # Nearby landmark
        for i, t in enumerate(tokens):
            if i in used_indices:
                continue
            if re.search(r'\b(nr\.?|near|opp\.?|opposite|behind|beside|adj\.?|adjacent)\b', t, re.IGNORECASE):
                nearby = t
                used_indices.add(i)
                break

        # Locality: first leftover token that's not city/state/pin
        for i, t in enumerate(tokens):
            if i in used_indices:
                continue
            lt = t.lower()
            city_val = result.get("city", "")
            state_val = result.get("state", "")
            pin_val = result.get("pin_code", "")
            if city_val and city_val.lower() in lt:
                used_indices.add(i)
                continue
            if state_val and state_val.lower() in lt:
                used_indices.add(i)
                continue
            if pin_val and pin_val in t:
                used_indices.add(i)
                continue
            if len(t) < 3:
                continue
            locality = t
            used_indices.add(i)
            break

    # Populate result dict
    if building_flat:
        result["building_flat_no"] = building_flat.strip()
    if premises_name:
        result["premises_name"] = premises_name.strip()
    if road_street:
        result["road_street"] = road_street.strip()
    if nearby:
        result["nearby_landmark"] = nearby.strip()
    if locality:
        result["locality"] = locality.strip()

    return result


def extract_gst_certificate_fields(raw_text: str) -> dict:
    """
    Extract fields from GST Certificate (Form GST REG-06).
    
    Args:
        raw_text: OCR extracted text from GST certificate
        
    Returns:
        Dictionary containing document_type, fields, missing_fields, and debug info
    """
    if not raw_text or not isinstance(raw_text, str):
        return _empty_result()
    
    cleaned_text = _normalize_text(raw_text)
    
    # Initialize fields with empty defaults
    extracted_fields = {
        "name": "",
        "constitution_of_business": "",
        "principal_address": "",
        "particulars_of_approving_authority": "",
        "gst_number": "",
        "total_no_of_additional_places": "",
        "additional_place_of_business": ""
    }
    
    # Extract each field
    extracted_fields["gst_number"] = _extract_gst_number(cleaned_text)
    extracted_fields["name"] = _extract_name(cleaned_text)
    extracted_fields["constitution_of_business"] = _extract_constitution(cleaned_text)
    extracted_fields["principal_address"] = _extract_principal_address(cleaned_text)
    extracted_fields["particulars_of_approving_authority"] = _extract_approving_authority(cleaned_text)
    extracted_fields["total_no_of_additional_places"] = _extract_total_additional_places(cleaned_text)
    
    # Handle additional places based on total count
    total_places = extracted_fields["total_no_of_additional_places"]
    if total_places == "0":
        extracted_fields["additional_place_of_business"] = "NA"
    else:
        extracted_fields["additional_place_of_business"] = _extract_additional_places(cleaned_text)

    # Post-process: normalize and structure final values
    fields = _post_process_fields(extracted_fields)

    # Identify missing fields (empty dict counts as missing for principal_address)
    missing_fields = []
    for key, value in fields.items():
        if key == "principal_address":
            # Empty dict or no keys means missing
            if not value or (isinstance(value, dict) and len(value) == 0):
                missing_fields.append(key)
        else:
            if not value or value == "":
                missing_fields.append(key)

    return {
        "document_type": "GST_CERTIFICATE",
        "fields": fields,
        "missing_fields": missing_fields,
        "debug": {
            "raw_text_length": len(raw_text),
            "text_preview": raw_text[:300] if raw_text else ""
        }
    }


def _validate_and_clean_fields(fields: Dict[str, str], text: str) -> Dict[str, str]:
    """
    Validate and clean extracted fields with multiple passes.
    """
    validated = fields.copy()
    
    if validated["name"]:
        validated["name"] = _validate_name(validated["name"])
    
    if validated["constitution_of_business"]:
        validated["constitution_of_business"] = _validate_constitution(validated["constitution_of_business"])
    elif not validated["constitution_of_business"]:
        validated["constitution_of_business"] = _fallback_constitution_extraction(text)
    
    if validated["principal_address"]:
        validated["principal_address"] = _validate_address(validated["principal_address"])
    elif not validated["principal_address"]:
        validated["principal_address"] = _fallback_address_extraction(text)
    
    if validated["particulars_of_approving_authority"]:
        validated["particulars_of_approving_authority"] = _validate_authority(validated["particulars_of_approving_authority"])
    
    if validated["gst_number"]:
        validated["gst_number"] = _validate_gstin(validated["gst_number"])
    
    if validated["total_no_of_additional_places"]:
        validated["total_no_of_additional_places"] = _validate_total_places(validated["total_no_of_additional_places"])
    
    if validated["additional_place_of_business"] and validated["additional_place_of_business"] != "NA":
        validated["additional_place_of_business"] = _validate_additional_places(validated["additional_place_of_business"])
    
    return validated


def _validate_name(name: str) -> str:
    """Validate extracted name."""
    if not name or len(name) < 3:
        return ""
    
    if _is_header_noise(name):
        return ""
    
    name = re.sub(r'\s+', ' ', name).strip()
    
    if re.match(r'^[A-Z\s\.\,\&\(\)\-]+$', name) and len(name) > 5:
        return name
    
    return name


def _validate_constitution(constitution: str) -> str:
    """Validate constitution value."""
    valid_types = [
        "proprietorship", "private limited", "public limited", "partnership",
        "llp", "society", "trust", "huf", "company", "limited liability partnership"
    ]
    
    constitution_lower = constitution.lower()
    for valid_type in valid_types:
        if valid_type in constitution_lower:
            return constitution
    
    return ""


def _validate_address(address: str) -> str:
    """Validate address field."""
    if not address or len(address) < 15:
        return ""
    
    if _contains_form_noise(address):
        return ""
    
    return address


def _validate_authority(authority: str) -> str:
    """Validate approving authority."""
    if not authority or len(authority) < 10:
        return ""
    
    if "goods and services tax act" in authority.lower() and re.search(r'\d{4}', authority):
        return authority
    
    return ""


def _validate_gstin(gstin: str) -> str:
    """Validate GSTIN format."""
    if not gstin or len(gstin) != 15:
        return ""
    
    pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$'
    if re.match(pattern, gstin):
        return gstin
    
    return ""


def _validate_total_places(total: str) -> str:
    """Validate total places count."""
    if not total:
        return ""
    
    if total.isdigit():
        num = int(total)
        if 0 <= num <= 100:
            return str(num)
    
    return ""


def _validate_additional_places(places: str) -> str:
    """Validate additional places field."""
    if not places or places == "NA":
        return places
    
    if _contains_form_noise(places):
        return ""
    
    if len(places) < 15:
        return ""
    
    return places


def _contains_form_noise(text: str) -> bool:
    """Check if text contains form headers or noise."""
    noise_indicators = [
        "goods and services tax identification number",
        "details of",
        "legal name",
        "trade name, if any",
        "form gst",
        "registration certificate",
        "annexure"
    ]
    
    text_lower = text.lower()
    for indicator in noise_indicators:
        if indicator in text_lower:
            return True
    
    return False


def _fallback_constitution_extraction(text: str) -> str:
    """Fallback method for constitution extraction with aggressive patterns."""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if re.search(r'constitution\s*(?:of\s*)?(?:business|bu\w*)', line, re.IGNORECASE):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                normalized = _normalize_constitution(next_line)
                if normalized and _validate_constitution(normalized):
                    return normalized
            
            if i + 2 < len(lines):
                next_next_line = lines[i + 2].strip()
                normalized = _normalize_constitution(next_next_line)
                if normalized and _validate_constitution(normalized):
                    return normalized
    
    pattern = r'constitution[^a-z]{0,50}(proprietorship|private\s*limited?|public\s*limited?|partnership|llp|society|trust|huf|company)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return _normalize_constitution(match.group(1))
    
    return ""


def _fallback_address_extraction(text: str) -> str:
    """Fallback method for address extraction with section-based parsing."""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if re.search(r'(?:address\s*of\s*)?principal\s*place', line, re.IGNORECASE):
            address_parts = []
            j = i + 1
            while j < len(lines) and j < i + 15:
                potential_line = lines[j].strip()
                
                if not potential_line or len(potential_line) < 3:
                    j += 1
                    continue
                
                if re.match(r'^\d+\s*\.', potential_line):
                    break
                
                if re.search(r'date\s*of\s*liability|validity|type\s*of\s*registration|particulars|approving', potential_line, re.IGNORECASE):
                    break
                
                if not _is_noise(potential_line) and not _is_header_noise(potential_line):
                    address_parts.append(potential_line)
                
                j += 1
            
            if address_parts:
                address = ', '.join(address_parts)
                address = _clean_address(address)
                if len(address) > 15:
                    return address
    
    pattern = r'principal\s*place[^\n]{0,30}\n((?:(?!\n\s*\d+\s*\.|date\s*of|validity|type\s*of).)+)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        address = match.group(1).strip()
        address = _clean_address(address)
        if len(address) > 15:
            return address
    
    return ""


def _empty_result() -> dict:
    """Return empty result structure."""
    return {
        "document_type": "GST_CERTIFICATE",
        "fields": {
            "name": "",
            "constitution_of_business": "",
            "principal_address": {},
            "particulars_of_approving_authority": "",
            "gst_number": "",
            "total_no_of_additional_places": "",
            "additional_place_of_business": ""
        },
        "missing_fields": [
            "name", "constitution_of_business", "principal_address",
            "particulars_of_approving_authority", "gst_number",
            "total_no_of_additional_places", "additional_place_of_business"
        ],
        "debug": {
            "raw_text_length": 0,
            "text_preview": ""
        }
    }


def _normalize_text(text: str) -> str:
    """Normalize whitespace and clean OCR artifacts."""
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(lines)


def _extract_name(text: str) -> str:
    """Extract Legal Name with fallback to Trade Name."""
    legal_name = _extract_legal_name(text)
    if legal_name and len(legal_name) > 3:
        return legal_name
    
    trade_name = _extract_trade_name(text)
    return trade_name if trade_name and len(trade_name) > 3 else ""


def _extract_legal_name(text: str) -> str:
    """Extract Legal Name from section 1."""
    lines = text.split('\n')
    
    # Method 1: Look for "Legal Name" header and get the next non-header line
    for i, line in enumerate(lines):
        if re.search(r'^legal\s*name\s*$', line, re.IGNORECASE):
            # Look at next lines for the actual name
            for offset in range(1, 4):
                if i + offset < len(lines):
                    candidate = lines[i + offset].strip()
                    # Skip if it's another header or empty
                    if not candidate or len(candidate) < 3:
                        continue
                    if _is_header_noise(candidate):
                        continue
                    # Skip if it looks like another section number
                    if re.match(r'^\d+\.?$', candidate):
                        continue
                    # This should be the name
                    candidate = re.sub(r'\s+', ' ', candidate)
                    if re.match(r'^[A-Z]', candidate) and not re.match(r'^Registration', candidate, re.IGNORECASE):
                        return candidate
    
    # Method 2: Look for section "1." pattern
    for i, line in enumerate(lines):
        if re.match(r'^\s*1\s*\.\s*$', line):
            # Skip the "Legal Name" header if present and get actual name
            for offset in range(1, 5):
                if i + offset < len(lines):
                    candidate = lines[i + offset].strip()
                    if not candidate or len(candidate) < 3:
                        continue
                    # Skip "Legal Name" header
                    if re.search(r'^legal\s*name', candidate, re.IGNORECASE):
                        continue
                    if _is_header_noise(candidate):
                        continue
                    if re.match(r'^\d+\.?$', candidate):
                        continue
                    candidate = re.sub(r'\s+', ' ', candidate)
                    if re.match(r'^[A-Z]', candidate) and not re.match(r'^Registration', candidate, re.IGNORECASE):
                        return candidate
    
    # Method 3: Direct regex pattern after Registration Number
    pattern = r'Registration\s*Number\s*[:\-]?\s*[A-Z0-9]+\s*\n.*?Legal\s*Name\s*\n\s*([A-Z][A-Z\s\.\,\&\(\)\-]+(?:LTD|LIMITED|LLP|COMPANY|ENTERPRISE|CORP|PRIVATE|PVT)[A-Z\s\.]*?)\s*\n'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        name = match.group(1).strip()
        name = re.sub(r'\s+', ' ', name)
        if not _is_header_noise(name):
            return name
    
    return ""


def _extract_trade_name(text: str) -> str:
    """Extract Trade Name as fallback."""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if re.match(r'^\s*2\s*\.?\s*$', line) or re.search(r'^trade\s*name', line, re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if candidate and len(candidate) > 3 and not _is_header_noise(candidate):
                    candidate = re.sub(r'\s+', ' ', candidate)
                    if re.match(r'^[A-Z]', candidate):
                        return candidate
    
    return ""


def _extract_constitution(text: str) -> str:
    """Extract Constitution of Business."""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if re.search(r'(?:3|4)\s*\.?\s*$', line) or re.search(r'^constitution\s*(?:of\s*)?(?:business|bu\w*)', line, re.IGNORECASE):
            for offset in [1, 2]:
                if i + offset < len(lines):
                    candidate = lines[i + offset].strip()
                    normalized = _normalize_constitution(candidate)
                    if normalized and len(normalized) > 2:
                        return normalized
    
    pattern = r'constitution\s*(?:of\s*)?(?:business|bu\w*)\s*\n\s*([\w\s\/]+?)(?=\n|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        constitution = match.group(1).strip()
        return _normalize_constitution(constitution)
    
    return ""


def _normalize_constitution(value: str) -> str:
    """Normalize constitution values."""
    if not value:
        return ""
    
    value = re.sub(r'\s+', ' ', value).strip()
    value_lower = value.lower()
    
    if 'private' in value_lower and 'limit' in value_lower:
        return "Private Limited"
    elif 'public' in value_lower and 'limit' in value_lower:
        return "Public Limited"
    elif 'llp' in value_lower or 'limited liability partnership' in value_lower:
        return "LLP"
    elif 'partnership' in value_lower and 'llp' not in value_lower and 'limited' not in value_lower:
        return "Partnership"
    elif 'proprietor' in value_lower:
        return "Proprietorship"
    elif 'society' in value_lower or 'club' in value_lower or 'aop' in value_lower:
        return "Society"
    elif 'trust' in value_lower:
        return "Trust"
    elif 'huf' in value_lower or 'hindu undivided family' in value_lower:
        return "HUF"
    elif 'company' in value_lower:
        return "Company"
    
    return ""


def _extract_principal_address(text: str) -> str:
    """Extract Principal Place of Business address."""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Match "Address of Principal Place" header (different from section numbers which vary)
        if re.search(r'(?:address\s*of\s*)?principal\s*place', line, re.IGNORECASE):
            address_parts = []
            j = i + 1
            
            # Skip header lines - these can be multi-word like "Address of Principal Place of"
            while j < len(lines) and j < i + 5:
                potential = lines[j].strip()
                # Skip if it's a header line (contains header keywords but no address data)
                if re.search(r'^(address\s*of|principal|place\s*of|business)$', potential, re.IGNORECASE):
                    j += 1
                    continue
                # Also skip lines that are clearly part of the header label
                if re.search(r'address\s*of\s*principal', potential, re.IGNORECASE):
                    j += 1
                    continue
                break
            
            while j < len(lines) and j < i + 20:
                potential_line = lines[j].strip()
                
                if not potential_line or len(potential_line) < 2:
                    j += 1
                    continue
                
                # Stop at next section number
                if re.match(r'^\d+\s*\.', potential_line):
                    break
                
                stop_keywords = [
                    r'^date\s*of\s*liability',
                    r'^date\s*of\s*validity',
                    r'^period\s*of\s*validity',
                    r'^type\s*of\s*registration',
                    r'^particulars\s*of',
                    r'^approving\s*authority',
                    r'^signature\s*$',  # Only standalone "Signature"
                    r'^annexure'
                ]
                
                if any(re.match(kw, potential_line, re.IGNORECASE) for kw in stop_keywords):
                    break
                
                # Skip standalone "Business" line (split header)
                if re.match(r'^business$', potential_line, re.IGNORECASE):
                    j += 1
                    continue
                
                # Skip header-like lines
                if _is_header_noise(potential_line):
                    j += 1
                    continue
                
                if not _is_noise(potential_line):
                    address_parts.append(potential_line)
                
                j += 1
            
            if address_parts:
                # Use newlines to preserve fragment structure for merging
                # The _structure_principal_address will handle the merging
                address = '\n'.join(address_parts)
                # Don't clean yet - let _structure_principal_address handle it
                if len(address) > 10 and not _contains_form_noise(address):
                    return address
    
    return ""


def _clean_address(address: str) -> str:
    """Clean and format address text."""
    address = re.sub(r'\s+', ' ', address)
    address = re.sub(r'\s*,\s*', ', ', address)
    address = re.sub(r',{2,}', ',', address)
    address = re.sub(r'^[,\s]+|[,\s]+$', '', address)
    
    parts = [p.strip() for p in address.split(',')]
    parts = [p for p in parts if p and len(p) > 1 and not _is_noise(p)]
    
    return ', '.join(parts)


def _extract_approving_authority(text: str) -> str:
    """
    Extract Particulars of Approving Authority.
    
    GST certificates may contain either:
    1. A reference to the Act (e.g., "Gujarat Goods and Services Tax Act, 2017")
    2. Officer details (Name, Designation, Jurisdictional Office)
    3. Digital signature information mentioning GST Network
    """
    lines = text.split('\n')
    
    # Method 1: Look for "Particulars of Approving" section and extract officer details
    for i, line in enumerate(lines):
        if re.search(r'particulars\s*of\s*approving', line, re.IGNORECASE):
            # Collect the next several lines to build officer details
            officer_parts = []
            name = ""
            designation = ""
            jurisdiction = ""
            
            for offset in range(1, 15):
                if i + offset < len(lines):
                    candidate = lines[i + offset].strip()
                    
                    # Stop if we hit next section markers
                    if re.search(r'date\s*of\s*issue|note:|annexure', candidate, re.IGNORECASE):
                        break
                    
                    # Check for GST Act mention
                    if re.search(r'goods\s*and\s*services\s*tax\s*act', candidate, re.IGNORECASE) and re.search(r'\d{4}', candidate):
                        return re.sub(r'\s+', ' ', candidate)
                    
                    # Extract Name after "Name" header
                    if 'Name' in lines[i + offset - 1] if i + offset - 1 >= 0 else False:
                        if candidate and not re.match(r'^(signature|designation|jurisdictional|date)', candidate, re.IGNORECASE):
                            name = candidate
                    
                    # Extract Designation
                    if 'Designation' in candidate:
                        if i + offset + 1 < len(lines):
                            designation = lines[i + offset + 1].strip()
                    
                    # Extract Jurisdictional Office
                    if re.search(r'Jurisdictional\s*Office', candidate, re.IGNORECASE):
                        if i + offset + 1 < len(lines):
                            jurisdiction = lines[i + offset + 1].strip()
            
            # Build authority string from officer details
            if name or designation or jurisdiction:
                parts = []
                if name and not re.match(r'^(centre|center|signature)$', name, re.IGNORECASE):
                    parts.append(name)
                if designation:
                    parts.append(designation)
                if jurisdiction:
                    parts.append(f"({jurisdiction})")
                if parts:
                    return " - ".join(parts)
    
    # Method 2: Look for section 9 with officer details
    for i, line in enumerate(lines):
        if re.match(r'^\s*9\s*\.?\s*$', line):
            # Look for name and designation in following lines
            for offset in range(1, 12):
                if i + offset < len(lines):
                    if 'Name' in lines[i + offset]:
                        if i + offset + 1 < len(lines):
                            officer_name = lines[i + offset + 1].strip()
                            if officer_name and len(officer_name) > 2:
                                # Try to get designation
                                for j in range(offset + 2, offset + 6):
                                    if i + j < len(lines) and 'Designation' in lines[i + j]:
                                        if i + j + 1 < len(lines):
                                            designation = lines[i + j + 1].strip()
                                            return f"{officer_name} - {designation}"
                                return officer_name
    
    # Method 3: Look for digital signature with GST Network reference
    ds_match = re.search(
        r'(?:digitally\s+signed\s+by\s+)?DS\s+GOODS\s+AND\s+SERVICES\s+TAX\s+NETWORK',
        text, re.IGNORECASE
    )
    if ds_match:
        return "Goods and Services Tax Network (Digital Signature)"
    
    # Method 4: Direct pattern - State/Central GST Act with year
    pattern = r'((?:central|state|union\s*territory|gujarat|maharashtra|karnataka|tamil\s*nadu|delhi|west\s*bengal|rajasthan|uttar\s*pradesh|madhya\s*pradesh|haryana|punjab|kerala|andhra\s*pradesh|telangana|bihar|odisha|assam|jharkhand|chhattisgarh|goa|himachal\s*pradesh|uttarakhand|jammu|ladakh|puducherry|chandigarh)\s+goods\s*and\s*services\s*tax\s*act\s*,?\s*\d{4})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        authority = match.group(1).strip()
        return re.sub(r'\s+', ' ', authority)
    
    # Method 5: Look for CGST/SGST/IGST/UTGST Act pattern
    cgst_pattern = r'((?:cgst|sgst|igst|utgst)\s*act\s*,?\s*\d{4})'
    match = re.search(cgst_pattern, text, re.IGNORECASE)
    if match:
        authority = match.group(1).strip().upper()
        return re.sub(r'\s+', ' ', authority)
    
    # Method 6: Generic GST Act pattern
    pattern = r'(goods\s*and\s*services\s*tax\s*act\s*,?\s*\d{4})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        authority = match.group(1).strip()
        return re.sub(r'\s+', ' ', authority).title()
    
    # Method 7: Look for "issued under" or "granted under" context
    issued_pattern = r'(?:issued|granted|approved)\s+(?:under|as\s+per)\s+(?:the\s+)?([^\n]*?(?:act|acts)[^\n]*?\d{4})'
    match = re.search(issued_pattern, text, re.IGNORECASE)
    if match:
        authority = match.group(1).strip()
        # Clean up common noise
        authority = re.sub(r'^(?:the\s+)?', '', authority, flags=re.IGNORECASE)
        if len(authority) > 10:
            return re.sub(r'\s+', ' ', authority)
    
    # Method 8: Look for "jurisdictional authority" mention
    if re.search(r'by\s+the\s+jurisdictional\s+authority', text, re.IGNORECASE):
        # Try to find the jurisdiction name
        jurisdiction_match = re.search(r'Jurisdictional\s*Office\s*\n\s*([A-Z][A-Z\s]+)', text)
        if jurisdiction_match:
            return f"Jurisdictional Authority - {jurisdiction_match.group(1).strip()}"
        return "Jurisdictional Authority"
    
    return ""


def _extract_gst_number(text: str) -> str:
    """Extract GSTIN (15-character format)."""
    pattern = r'\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1})\b'
    
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    
    pattern_flexible = r'(?:gstin|gst\s*no|registration\s*number|identification\s*number)[:\s\-]*([A-Z0-9]{15})'
    match = re.search(pattern_flexible, text, re.IGNORECASE)
    if match:
        gstin = match.group(1).upper().replace(' ', '')
        if len(gstin) == 15 and re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z\d]{3}$', gstin):
            return gstin
    
    return ""


def _extract_total_additional_places(text: str) -> str:
    """Extract total number of additional places of business."""
    pattern = r'total\s*(?:no\.?|number)\s*of\s*additional\s*places?\s*(?:of\s*business)?\s*(?:in\s*the\s*state)?\s*[:\-]?\s*(\d+)'
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'total\s*number\s*of\s*additional', line, re.IGNORECASE):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.isdigit():
                    return next_line
            
            digit_match = re.search(r'\b(\d+)\b', line)
            if digit_match:
                return digit_match.group(1)
    
    if re.search(r'annexure\s*[:\-]?\s*a', text, re.IGNORECASE):
        annexure_match = re.search(r'annexure\s*[:\-]?\s*a.*?total.*?(\d+)', text, re.IGNORECASE | re.DOTALL)
        if annexure_match:
            return annexure_match.group(1)
    
    return ""


def _extract_additional_places(text: str) -> str:
    """Extract additional places of business from Annexure A."""
    # Find Annexure A section, stop before Annexure B or signature
    annexure_pattern = r'annexure\s*[:\-]?\s*a\s*(.*?)(?=\bannexure\s*[:\-]?\s*b\b|signature|note\s*[::]|\Z)'
    
    match = re.search(annexure_pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    
    annexure_text = match.group(1).strip()
    
    if len(annexure_text) < 30:
        return ""
    
    # Check for zero additional places
    if "total number of additional places" in annexure_text.lower():
        zero_check = re.search(r'total\s*number.*?(\d+)', annexure_text, re.IGNORECASE)
        if zero_check and zero_check.group(1) == "0":
            return ""
    
    addresses = _parse_annexure_addresses(annexure_text)
    
    if addresses:
        return '\n\n'.join(addresses)
    
    return ""


def _parse_annexure_addresses(text: str) -> List[str]:
    """Parse addresses from Annexure A section."""
    
    # Get company name/trade name to filter them out later
    company_names = set()
    name_match = re.search(r'legal\s*name\s*\n\s*([^\n]+)', text, re.IGNORECASE)
    if name_match:
        company_names.add(name_match.group(1).strip().lower())
    trade_match = re.search(r'trade\s*name.*?\n\s*([^\n]+)', text, re.IGNORECASE)
    if trade_match:
        company_names.add(trade_match.group(1).strip().lower())
    
    # Remove header noise patterns
    noise_patterns = [
        r'annexure\s*[:\-]?\s*a',
        r'details\s*of\s*additional\s*place(?:s)?\s*of\s*business(?:\(s\))?',
        r'additional\s*place(?:s)?\s*of\s*business',
        r'goods\s*and\s*services\s*tax\s*identification\s*number',
        r'\bgstin\b',
        r'legal\s*name',
        r'trade\s*name.*?if\s*any',
        r'trade\s*name',
        r'total\s*number\s*of\s*additional\s*places?\s*of\s*business(?:\(s\))?\s*in\s*the\s*state',
        r'total\s*number\s*of\s*\(s\)\s*in\s*the\s*state',
        r'sr\.?\s*no\.?',
        r's\.?\s*no\.?',
        r'serial\s*no\.?',
        r'\baddress\b',  # Remove standalone "Address" header
        r'for[,\s]+[A-Z][A-Z\s\.\-]+(?:pvt\.?|private|ltd\.?|limited|llp)+[,\.\s]*',  # "FOR, COMPANY NAME"
        r'authorised\s*/?\s*director',
        r'authorized\s*/?\s*director',
        r'\d{2}[A-Z]{5}\d{4}[A-Z\d]{3}',  # GSTIN pattern
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    addresses = []
    current_address = []
    in_address = False
    
    for line in lines:
        line = line.strip()
        
        if not line or len(line) < 3:
            continue
        
        # Skip if line contains form noise
        if _contains_form_noise(line):
            continue
        
        # Skip if line is exactly a company name we extracted
        if line.lower() in company_names:
            continue
            
        # Skip lines that look like company names (all caps with Ltd/Pvt/LLP)
        if re.match(r'^[A-Z][A-Z\s\.\-]+(?:PRIVATE\s+LIMITED|PVT\.?\s*LTD\.?|LIMITED|LLP)$', line, re.IGNORECASE):
            continue
        
        # Skip random OCR noise (short gibberish, numbers only that aren't section markers)
        if len(line) < 5 and not re.match(r'^\d+$', line):
            continue
        if re.match(r'^[^a-zA-Z]*$', line) and len(line) < 10:
            continue
        
        # Check for numbered address entry (1, 2, 3 etc)
        numbered = re.match(r'^(\d+)$', line)
        if numbered:
            # Save previous address if exists
            if current_address:
                addr = _clean_additional_address(current_address, company_names)
                if addr:
                    addresses.append(addr)
            current_address = []
            in_address = True
            continue
        
        # Add line to current address if we're collecting
        if in_address or _looks_like_address(line):
            in_address = True
            # Skip lines that are just noise at start
            if not current_address and _is_noise(line):
                continue
            current_address.append(line)
    
    # Save last address
    if current_address:
        addr = _clean_additional_address(current_address, company_names)
        if addr:
            addresses.append(addr)
    
    return addresses[:20]


def _looks_like_address(line: str) -> bool:
    """Check if a line looks like it's part of an address."""
    address_indicators = [
        r'survey\s*no',
        r'plot\s*no', 
        r'building',
        r'flat\s*no',
        r'floor',
        r'road',
        r'street',
        r'taluka',
        r'village',
        r'\b\d{6}\b',  # PIN code
        r'\bgujarat\b',
        r'\bmaharashtra\b',
        r'\bahmedabad\b',
        r'\bmumbai\b',
    ]
    line_lower = line.lower()
    return any(re.search(p, line_lower) for p in address_indicators)


def _clean_additional_address(lines: List[str], company_names: set) -> str:
    """Clean and join address lines, removing noise."""
    cleaned = []
    for line in lines:
        line = line.strip()
        # Skip company names
        if line.lower() in company_names:
            continue
        # Skip company-like patterns
        if re.match(r'^[A-Z][A-Z\s\.\-]+(?:PRIVATE\s+LIMITED|PVT\.?\s*LTD\.?|LIMITED|LLP)$', line, re.IGNORECASE):
            continue
        # Skip FOR, COMPANY footer patterns
        if re.match(r'^for[,\s]*', line, re.IGNORECASE):
            continue
        # Skip if just noise
        if _is_noise(line):
            continue
        cleaned.append(line)
    
    if not cleaned:
        return ""
    
    # Join with comma if parts don't already end with comma
    result_parts = []
    for part in cleaned:
        part = part.rstrip(',').strip()
        if part:
            result_parts.append(part)
    
    result = ', '.join(result_parts)
    
    # Clean up multiple commas and whitespace
    result = re.sub(r',\s*,+', ',', result)
    result = re.sub(r'\s+', ' ', result)
    result = result.strip(' ,')
    
    # Remove trailing OCR noise (short random text after state/PIN)
    # Pattern: keep up to PIN code, remove random gibberish after
    pin_match = re.search(r'(\d{6})\s*[,\s]*(.*)$', result)
    if pin_match:
        trailing = pin_match.group(2).strip()
        # If trailing part is short and doesn't look meaningful, remove it
        if len(trailing) < 15 and not re.search(r'\b(road|street|taluka|village|district)\b', trailing, re.IGNORECASE):
            result = result[:pin_match.end(1)]
    
    # Must have minimum length and look like an address
    if len(result) < 20:
        return ""
    if not _looks_like_address(result):
        return ""
    
    return result


def _clean_field_value(value: str) -> str:
    """Clean extracted field value."""
    value = re.sub(r'\s+', ' ', value)
    value = re.sub(r'[:\-]+\s*$', '', value)
    value = re.sub(r'^\s*[:\-]+', '', value)
    value = re.sub(r'^[,\s]+|[,\s]+$', '', value)
    return value.strip()


def _is_noise(text: str) -> bool:
    """Check if text is likely OCR noise."""
    if not text or len(text) < 2:
        return True
    
    noise_patterns = [
        r'^[^a-zA-Z0-9]+$',
        r'^(yes|no|na|nil)$',
        r'^\d+\s*\.\s*$',
        r'^page\s*\d+',
        r'^\d{1,4}$',  # Only 1-4 digit numbers are noise (not 6-digit PIN codes)
    ]
    
    for pattern in noise_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    
    return False


def _is_header_noise(text: str) -> bool:
    """Check if text is a form header or label."""
    header_patterns = [
        r'trade\s*name.*if\s*any',
        r'^legal\s*name$',
        r'^trade\s*name$',
        r'form\s*gst',
        r'government\s*of\s*india',
        r'registration\s*certificate',
        r'goods\s*and\s*services',
        r'^details\s*of',
        r'^constitution\s*of',
        r'^principal\s*place',
        r'^address\s*of',
        r'additional.*if\s*any',
        r'see\s*rule',
    ]
    
    for pattern in header_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
