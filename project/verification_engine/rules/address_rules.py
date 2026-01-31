"""
Address Matching Rules

Compare addresses across GST and Udyam documents.
Checks both registered office and factory/plant addresses.
"""

from typing import Dict, List
from .base_rule import BaseRule, RuleResult, Severity, Status


class AddressGstPrincipalUdyamOffice(BaseRule):
    """Verify GST principal address matches Udyam registered office address."""
    
    @property
    def rule_id(self) -> str:
        return "ADDR_GST_PRINCIPAL_UDYAM_OFFICE"
    
    @property
    def description(self) -> str:
        return "GST principal place of business should match Udyam registered office address"
    
    @property
    def severity(self) -> Severity:
        return Severity.WARNING
    
    @property
    def source_docs(self) -> List[str]:
        return ["GST", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing GST or Udyam data")
        
        gst_addr = entity["gst"].get("principal_address", {})
        udyam_addr = entity["udyam"].get("registered_address", {})
        
        if not gst_addr or not udyam_addr:
            return self.skip_result("Address data missing from one or both documents")
        
        # Calculate match score
        score, max_score, matches, mismatches = self._compare_addresses(gst_addr, udyam_addr)
        
        details = {
            "match_score": f"{score}/{max_score}",
            "gst_address": gst_addr.get("full_address", ""),
            "udyam_address": udyam_addr.get("full_address", ""),
            "matches": matches,
            "mismatches": mismatches
        }
        
        if score == max_score:
            return self.pass_result("GST principal address matches Udyam registered office", details)
        elif score >= max_score * 0.6:  # At least 60% match
            return self.warning_result(
                f"Partial address match ({score}/{max_score} fields)",
                details
            )
        else:
            return self.fail_result(
                f"Address mismatch ({score}/{max_score} fields match)",
                details
            )
    
    def _compare_addresses(self, addr1: Dict, addr2: Dict) -> tuple:
        """Compare two addresses field by field. Returns (score, max_score, matches, mismatches)."""
        fields = ["pin", "city", "district", "state", "locality"]
        score = 0
        max_score = 0
        matches = []
        mismatches = []
        
        for field in fields:
            val1 = addr1.get(field, "").upper().strip()
            val2 = addr2.get(field, "").upper().strip()
            
            if val1 or val2:  # Only compare if at least one has a value
                max_score += 1
                if val1 and val2 and val1 == val2:
                    score += 1
                    matches.append(f"{field}: {val1}")
                elif val1 and val2:
                    mismatches.append(f"{field}: GST='{val1}' vs Udyam='{val2}'")
        
        return score, max_score, matches, mismatches


class PinMatchGstUdyam(BaseRule):
    """Critical check: PIN codes must match between GST and Udyam."""
    
    @property
    def rule_id(self) -> str:
        return "PIN_MATCH_GST_UDYAM"
    
    @property
    def description(self) -> str:
        return "PIN code should match between GST principal address and Udyam registered office"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["GST", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing GST or Udyam data")
        
        gst_addr = entity["gst"].get("principal_address", {})
        udyam_addr = entity["udyam"].get("registered_address", {})
        
        gst_pin = gst_addr.get("pin", "").strip()
        udyam_pin = udyam_addr.get("pin", "").strip()
        
        if not gst_pin or not udyam_pin:
            return self.skip_result("PIN code missing from one or both documents")
        
        if gst_pin == udyam_pin:
            return self.pass_result(
                f"PIN codes match: {gst_pin}",
                {"gst_pin": gst_pin, "udyam_pin": udyam_pin}
            )
        else:
            return self.fail_result(
                "PIN codes do NOT match",
                {"gst_pin": gst_pin, "udyam_pin": udyam_pin}
            )


class AddressGstUdyamFactory(BaseRule):
    """Check if GST additional place matches any Udyam factory/unit address."""
    
    @property
    def rule_id(self) -> str:
        return "ADDR_GST_ADDITIONAL_UDYAM_FACTORY"
    
    @property
    def description(self) -> str:
        return "GST additional places of business should match Udyam unit/factory addresses"
    
    @property
    def severity(self) -> Severity:
        return Severity.INFO
    
    @property
    def source_docs(self) -> List[str]:
        return ["GST", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing GST or Udyam data")
        
        gst_additional = entity["gst"].get("additional_places", "")
        factory_addresses = entity["udyam"].get("factory_addresses", [])
        
        if not gst_additional:
            return self.skip_result("No additional places in GST")
        
        if not factory_addresses:
            return self.skip_result("No factory/unit addresses in Udyam")
        
        # Check if any factory PIN matches the additional places string
        gst_upper = gst_additional.upper()
        matches = []
        
        for factory in factory_addresses:
            pin = factory.get("pin", "")
            if pin and pin in gst_upper:
                matches.append({
                    "pin": pin,
                    "unit_name": factory.get("unit_name", "")
                })
        
        details = {
            "gst_additional_places": gst_additional,
            "udyam_factories": [f.get("full_address", "") for f in factory_addresses],
            "matching_pins": matches
        }
        
        if matches:
            return self.pass_result(
                f"Found {len(matches)} matching factory address(es) by PIN",
                details
            )
        else:
            return self.warning_result(
                "Could not match GST additional places with Udyam factory addresses",
                details
            )
