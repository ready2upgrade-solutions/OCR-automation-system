"""
PAN Document Adapter

Normalizes PAN card extracted data into canonical format.
"""

from typing import Dict
from .base_adapter import BaseAdapter


class PANAdapter(BaseAdapter):
    """Adapter for PAN card documents."""
    
    @property
    def document_type(self) -> str:
        return "PAN"
    
    def adapt(self, raw_data: Dict) -> Dict:
        """
        Transform raw PAN data into normalized format.
        
        Expected input structure:
        {
            "document_type": "PAN",
            "fields": {
                "pan": "ABFCS7205N",
                "pan_type": "COMPANY",
                "name": "STELLINOX STAINLESS PRIVATE LIMITED",
                "incorporation_date": "11/03/2021"
            }
        }
        
        Returns normalized structure with consistent keys.
        """
        fields = raw_data.get("fields", {})
        
        return {
            "source": self.document_type,
            "legal_name": self.normalize_text(fields.get("name", "")),
            "pan": self.normalize_pan(fields.get("pan", "")),
            "pan_type": fields.get("pan_type", "").upper().strip(),
            "incorporation_date": self.normalize_date(fields.get("incorporation_date")),
            "raw_name": fields.get("name", ""),  # Keep original for display
        }
