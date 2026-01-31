"""
Name Matching Rules

Cross-check legal names between PAN, GST, and Udyam documents.
"""

from typing import Dict, List
from .base_rule import BaseRule, RuleResult, Severity, Status


class NameMatchPanGst(BaseRule):
    """Verify name on PAN matches name on GST certificate."""
    
    @property
    def rule_id(self) -> str:
        return "NAME_MATCH_PAN_GST"
    
    @property
    def description(self) -> str:
        return "PAN legal name should match GST legal name"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["PAN", "GST"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing PAN or GST data")
        
        pan_name = entity["pan"].get("legal_name", "")
        gst_name = entity["gst"].get("legal_name", "")
        
        if not pan_name or not gst_name:
            return self.skip_result("Name field missing in one or both documents")
        
        if pan_name == gst_name:
            return self.pass_result(
                "PAN name matches GST name",
                {"pan_name": pan_name, "gst_name": gst_name}
            )
        else:
            return self.fail_result(
                "PAN name does NOT match GST name",
                {
                    "pan_name": pan_name,
                    "gst_name": gst_name,
                    "pan_raw": entity["pan"].get("raw_name", ""),
                    "gst_raw": entity["gst"].get("raw_name", "")
                }
            )


class NameMatchPanUdyam(BaseRule):
    """Verify name on PAN matches name on Udyam registration."""
    
    @property
    def rule_id(self) -> str:
        return "NAME_MATCH_PAN_UDYAM"
    
    @property
    def description(self) -> str:
        return "PAN legal name should match Udyam enterprise name"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["PAN", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing PAN or Udyam data")
        
        pan_name = entity["pan"].get("legal_name", "")
        udyam_name = entity["udyam"].get("legal_name", "")
        
        if not pan_name or not udyam_name:
            return self.skip_result("Name field missing in one or both documents")
        
        if pan_name == udyam_name:
            return self.pass_result(
                "PAN name matches Udyam name",
                {"pan_name": pan_name, "udyam_name": udyam_name}
            )
        else:
            return self.fail_result(
                "PAN name does NOT match Udyam name",
                {
                    "pan_name": pan_name,
                    "udyam_name": udyam_name,
                    "pan_raw": entity["pan"].get("raw_name", ""),
                    "udyam_raw": entity["udyam"].get("raw_name", "")
                }
            )


class NameMatchGstUdyam(BaseRule):
    """Verify name on GST matches name on Udyam registration."""
    
    @property
    def rule_id(self) -> str:
        return "NAME_MATCH_GST_UDYAM"
    
    @property
    def description(self) -> str:
        return "GST legal name should match Udyam enterprise name"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["GST", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing GST or Udyam data")
        
        gst_name = entity["gst"].get("legal_name", "")
        udyam_name = entity["udyam"].get("legal_name", "")
        
        if not gst_name or not udyam_name:
            return self.skip_result("Name field missing in one or both documents")
        
        if gst_name == udyam_name:
            return self.pass_result(
                "GST name matches Udyam name",
                {"gst_name": gst_name, "udyam_name": udyam_name}
            )
        else:
            return self.fail_result(
                "GST name does NOT match Udyam name",
                {
                    "gst_name": gst_name,
                    "udyam_name": udyam_name,
                    "gst_raw": entity["gst"].get("raw_name", ""),
                    "udyam_raw": entity["udyam"].get("raw_name", "")
                }
            )
