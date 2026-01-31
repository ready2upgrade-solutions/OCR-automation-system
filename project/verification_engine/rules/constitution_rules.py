"""
Constitution Matching Rules

Verify business constitution type consistency across documents.
"""

from typing import Dict, List
from .base_rule import BaseRule, RuleResult, Severity, Status


class ConstitutionGstUdyam(BaseRule):
    """Verify GST constitution matches Udyam enterprise type."""
    
    @property
    def rule_id(self) -> str:
        return "CONSTITUTION_GST_UDYAM"
    
    @property
    def description(self) -> str:
        return "GST constitution of business should be consistent with Udyam registration"
    
    @property
    def severity(self) -> Severity:
        return Severity.WARNING
    
    @property
    def source_docs(self) -> List[str]:
        return ["GST", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing GST or Udyam data")
        
        gst_constitution = entity["gst"].get("constitution", "")
        udyam_name = entity["udyam"].get("legal_name", "")
        udyam_raw = entity["udyam"].get("raw_name", "")
        
        if not gst_constitution:
            return self.skip_result("Constitution missing from GST certificate")
        
        # Infer constitution from Udyam name
        inferred_constitution = self._infer_constitution_from_name(udyam_raw or udyam_name)
        
        details = {
            "gst_constitution": gst_constitution,
            "gst_raw_constitution": entity["gst"].get("raw_constitution", ""),
            "inferred_from_udyam": inferred_constitution,
            "udyam_name": udyam_raw
        }
        
        if not inferred_constitution:
            return self.pass_result(
                "Could not infer constitution from Udyam name (check manually)",
                details
            )
        
        if gst_constitution == inferred_constitution:
            return self.pass_result(
                f"Constitution match: {gst_constitution}",
                details
            )
        else:
            return self.warning_result(
                f"Constitution may not match: GST='{gst_constitution}' vs inferred='{inferred_constitution}'",
                details
            )
    
    def _infer_constitution_from_name(self, name: str) -> str:
        """Infer business constitution from entity name."""
        if not name:
            return ""
        
        name_upper = name.upper()
        
        # Check for common patterns in name
        patterns = [
            ("PRIVATE LIMITED", ["PRIVATE LIMITED", "PVT LTD", "PVT. LTD.", "PRIVATE LTD"]),
            ("PUBLIC LIMITED", ["PUBLIC LIMITED", "PUBLIC LTD"]),
            ("LLP", ["LLP", "LIMITED LIABILITY PARTNERSHIP"]),
            ("PARTNERSHIP", ["PARTNERSHIP"]),
        ]
        
        for canonical, keywords in patterns:
            for keyword in keywords:
                if keyword in name_upper:
                    return canonical
        
        return ""
