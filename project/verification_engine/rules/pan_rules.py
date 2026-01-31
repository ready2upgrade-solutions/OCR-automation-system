"""
PAN Number Matching Rules

Verify PAN consistency across documents.
"""

from typing import Dict, List
from .base_rule import BaseRule, RuleResult, Severity, Status


class PanMatchGst(BaseRule):
    """Verify PAN number matches the PAN embedded in GST number."""
    
    @property
    def rule_id(self) -> str:
        return "PAN_MATCH_GST"
    
    @property
    def description(self) -> str:
        return "PAN number should match PAN portion of GST number (positions 3-12)"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["PAN", "GST"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing PAN or GST data")
        
        pan_number = entity["pan"].get("pan", "")
        gst_pan = entity["gst"].get("pan", "")  # Already extracted from GST number
        
        if not pan_number:
            return self.skip_result("PAN number missing from PAN document")
        
        if not gst_pan:
            return self.skip_result("Could not extract PAN from GST number")
        
        if pan_number == gst_pan:
            return self.pass_result(
                "PAN number matches GST",
                {"pan": pan_number, "gst_pan": gst_pan}
            )
        else:
            return self.fail_result(
                "PAN number does NOT match GST",
                {
                    "pan": pan_number,
                    "gst_pan": gst_pan,
                    "gst_number": entity["gst"].get("gst_number", "")
                }
            )


class PanMatchUdyam(BaseRule):
    """Verify PAN number matches PAN in Udyam registration."""
    
    @property
    def rule_id(self) -> str:
        return "PAN_MATCH_UDYAM"
    
    @property
    def description(self) -> str:
        return "PAN number should match PAN in Udyam registration"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["PAN", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing PAN or Udyam data")
        
        pan_number = entity["pan"].get("pan", "")
        udyam_pan = entity["udyam"].get("pan", "")
        
        if not pan_number:
            return self.skip_result("PAN number missing from PAN document")
        
        if not udyam_pan:
            return self.skip_result("PAN number missing from Udyam registration")
        
        if pan_number == udyam_pan:
            return self.pass_result(
                "PAN number matches Udyam",
                {"pan": pan_number, "udyam_pan": udyam_pan}
            )
        else:
            return self.fail_result(
                "PAN number does NOT match Udyam",
                {"pan": pan_number, "udyam_pan": udyam_pan}
            )
