"""
GST Certificate Adapter

Normalizes GST certificate extracted data into canonical format.
"""

from typing import Dict
from .base_adapter import BaseAdapter


class GSTAdapter(BaseAdapter):
    """Adapter for GST certificate documents."""
    
    @property
    def document_type(self) -> str:
        return "GST"
    
    def adapt(self, raw_data: Dict) -> Dict:
        """
        Transform raw GST data into normalized format.
        
        Expected input structure:
        {
            "document_type": "GST_CERTIFICATE",
            "fields": {
                "name": "STELLINOX STAINLESS PRIVATE LIMITED",
                "constitution_of_business": "Private Limited",
                "principal_address": {...},
                "gst_number": "24ABFCS7205N1Z3",
                "additional_place_of_business": "..."
            }
        }
        """
        fields = raw_data.get("fields", {})
        gst_number = fields.get("gst_number", "")
        
        # Extract PAN from GST number (positions 2-12)
        pan_from_gst = ""
        if gst_number and len(gst_number) >= 12:
            pan_from_gst = gst_number[2:12].upper()
        
        # Normalize principal address
        principal_addr = self.normalize_address(fields.get("principal_address", {}))
        
        return {
            "source": self.document_type,
            "legal_name": self.normalize_text(fields.get("name", "")),
            "pan": pan_from_gst,
            "gst_number": gst_number.upper().strip() if gst_number else "",
            "constitution": self.normalize_constitution(fields.get("constitution_of_business", "")),
            "principal_address": principal_addr,
            "additional_places": fields.get("additional_place_of_business", ""),
            "total_additional_places": fields.get("total_no_of_additional_places", "0"),
            "raw_name": fields.get("name", ""),  # Keep original for display
            "raw_constitution": fields.get("constitution_of_business", ""),
        }
