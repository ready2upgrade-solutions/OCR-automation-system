"""
Base Adapter Interface for Document Normalization

Adapters transform raw document JSON into normalized canonical format
for consistent cross-document verification.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import re


class BaseAdapter(ABC):
    """
    Abstract base class for document adapters.
    
    Each document type (PAN, GST, Udyam) has its own adapter 
    that normalizes the extracted fields into a common format.
    """
    
    @property
    @abstractmethod
    def document_type(self) -> str:
        """Document type identifier (e.g., 'PAN', 'GST', 'UDYAM')."""
        pass
    
    @abstractmethod
    def adapt(self, raw_data: Dict) -> Dict:
        """
        Transform raw document JSON into normalized format.
        
        Args:
            raw_data: Raw extracted document data
            
        Returns:
            Normalized data with consistent field names
        """
        pass
    
    # -------------------------
    # Utility Methods
    # -------------------------
    
    @staticmethod
    def normalize_text(value: Optional[str]) -> str:
        """
        Normalize text for comparison:
        - Convert to uppercase
        - Remove special characters except spaces
        - Strip whitespace
        - Remove common prefixes (M/S, M/s, Messrs, etc.)
        """
        if not value:
            return ""
        
        text = value.upper().strip()
        
        # Remove common business prefixes
        prefixes = [r"^M/S\.?\s*", r"^M/s\.?\s*", r"^MESSRS\.?\s*", r"^SHRI\s+", r"^SMT\.?\s*"]
        for prefix in prefixes:
            text = re.sub(prefix, "", text, flags=re.IGNORECASE)
        
        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r"[^A-Z0-9 ]", "", text)
        
        # Normalize multiple spaces to single
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    @staticmethod
    def normalize_pan(pan: Optional[str]) -> str:
        """Normalize PAN number: uppercase, strip whitespace."""
        if not pan:
            return ""
        return pan.strip().upper()
    
    @staticmethod
    def normalize_date(date_str: Optional[str]) -> str:
        """
        Normalize date string to DD/MM/YYYY format.
        Handles common formats like DD-MM-YYYY, DD.MM.YYYY
        """
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        # Replace common separators with /
        normalized = re.sub(r"[-.]", "/", date_str)
        return normalized
    
    @staticmethod
    def normalize_address(addr_dict: Optional[Dict]) -> Dict:
        """
        Normalize address dictionary to standard format.
        
        Returns:
            Dict with keys: flat_no, building, road, locality, city, 
                           district, state, pin, full_address
        """
        if not addr_dict:
            return {
                "flat_no": "",
                "building": "",
                "road": "",
                "locality": "",
                "city": "",
                "district": "",
                "state": "",
                "pin": "",
                "full_address": ""
            }
        
        # Common key mappings
        flat_keys = ["flat_no", "building_flat_no", "flat", "plot", "door_no"]
        building_keys = ["building", "premises_name", "premises", "complex"]
        road_keys = ["road", "road_street", "street", "lane"]
        locality_keys = ["locality", "area", "village_town", "village", "town"]
        city_keys = ["city", "taluka", "tehsil"]
        district_keys = ["district"]
        state_keys = ["state"]
        pin_keys = ["pin", "pin_code", "pincode", "postal_code"]
        
        def get_first_match(keys):
            for key in keys:
                if key in addr_dict and addr_dict[key]:
                    val = addr_dict[key]
                    if isinstance(val, str):
                        return val.strip().upper()
            return ""
        
        result = {
            "flat_no": get_first_match(flat_keys),
            "building": get_first_match(building_keys),
            "road": get_first_match(road_keys),
            "locality": get_first_match(locality_keys),
            "city": get_first_match(city_keys),
            "district": get_first_match(district_keys),
            "state": get_first_match(state_keys),
            "pin": get_first_match(pin_keys),
        }
        
        # Build full address string
        parts = [v for v in result.values() if v]
        result["full_address"] = ", ".join(parts)
        
        return result
    
    @staticmethod
    def normalize_constitution(constitution: Optional[str]) -> str:
        """
        Normalize business constitution to standard categories.
        Maps various representations to canonical forms.
        """
        if not constitution:
            return ""
        
        const_upper = constitution.upper().strip()
        
        # Mapping to canonical forms
        mappings = {
            "PRIVATE LIMITED": ["PRIVATE LIMITED", "PVT LTD", "PRIVATE LTD", "PRIVATE LIMITED COMPANY"],
            "PUBLIC LIMITED": ["PUBLIC LIMITED", "PUBLIC LTD", "PUBLIC LIMITED COMPANY"],
            "LLP": ["LLP", "LIMITED LIABILITY PARTNERSHIP"],
            "PARTNERSHIP": ["PARTNERSHIP", "PARTNERSHIP FIRM"],
            "PROPRIETORSHIP": ["PROPRIETORSHIP", "SOLE PROPRIETORSHIP", "PROPRIETOR"],
            "HUF": ["HUF", "HINDU UNDIVIDED FAMILY"],
            "TRUST": ["TRUST"],
            "SOCIETY": ["SOCIETY"],
            "AOP": ["AOP", "ASSOCIATION OF PERSONS"],
            "BOI": ["BOI", "BODY OF INDIVIDUALS"],
        }
        
        for canonical, variants in mappings.items():
            for variant in variants:
                if variant in const_upper:
                    return canonical
        
        return const_upper  # Return as-is if no match
