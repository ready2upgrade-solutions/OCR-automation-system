"""
Udyam Registration Adapter

Normalizes Udyam registration extracted data into canonical format.
"""

from typing import Dict, List
from .base_adapter import BaseAdapter


class UdyamAdapter(BaseAdapter):
    """Adapter for Udyam registration documents."""
    
    @property
    def document_type(self) -> str:
        return "UDYAM"
    
    def adapt(self, raw_data: Dict) -> Dict:
        """
        Transform raw Udyam data into normalized format.
        
        Expected input structure:
        {
            "document_type": "UDYAM",
            "fields": {
                "udyam_number": "UDYAM-GJ-01-0090271",
                "enterprise_name": "M/S STELLINOX STAINLESS PRIVATE LIMITED",
                "pan": "ABFCS7205N",
                "incorporation_date": "11/03/2021",
                "official_address": {...}
            },
            "tables": {
                "units_details": [...]
            }
        }
        """
        fields = raw_data.get("fields", {})
        tables = raw_data.get("tables", {})
        
        # Normalize official/registered address
        registered_addr = self.normalize_address(fields.get("official_address", {}))
        
        # Normalize plant/factory addresses from units_details
        factory_addresses = self._extract_factory_addresses(tables.get("units_details", []))
        
        # Determine enterprise type from classification history
        enterprise_type = self._get_current_enterprise_type(
            tables.get("classification_history", [])
        )
        
        return {
            "source": self.document_type,
            "legal_name": self.normalize_text(fields.get("enterprise_name", "")),
            "pan": self.normalize_pan(fields.get("pan", "")),
            "udyam_number": fields.get("udyam_number", "").strip(),
            "incorporation_date": self.normalize_date(fields.get("incorporation_date")),
            "commencement_date": self.normalize_date(fields.get("commencement_date")),
            "registered_address": registered_addr,
            "factory_addresses": factory_addresses,
            "enterprise_type": enterprise_type,
            "mobile": fields.get("mobile", ""),
            "email": fields.get("email", ""),
            "raw_name": fields.get("enterprise_name", ""),  # Keep original for display
        }
    
    def _extract_factory_addresses(self, units_details: List[Dict]) -> List[Dict]:
        """Extract and normalize factory/plant addresses from units table."""
        addresses = []
        for unit in units_details:
            # Build address dict from unit fields
            addr_dict = {
                "flat_no": unit.get("flat", ""),
                "building": unit.get("building", ""),
                "village_town": unit.get("village_town", ""),
                "road": unit.get("road", ""),
                "pin": unit.get("pin", ""),
                "state": unit.get("state", ""),
                "district": unit.get("district", ""),
            }
            normalized = self.normalize_address(addr_dict)
            normalized["unit_name"] = unit.get("unit_name", "").replace("\n", " ").strip()
            addresses.append(normalized)
        return addresses
    
    def _get_current_enterprise_type(self, classification_history: List[Dict]) -> str:
        """Get the most recent enterprise classification (MICRO, SMALL, MEDIUM)."""
        if not classification_history:
            return ""
        
        # Sort by classification year descending to get most recent
        sorted_history = sorted(
            classification_history,
            key=lambda x: x.get("classification_year", "0000-00"),
            reverse=True
        )
        
        if sorted_history:
            return sorted_history[0].get("enterprise_type", "").upper()
        return ""
