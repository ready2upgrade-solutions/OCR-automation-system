"""
Date Verification Rules

Check incorporation dates and determine entity age/status.
"""

from typing import Dict, List
from datetime import datetime
from .base_rule import BaseRule, RuleResult, Severity, Status


class IncorporationDateMatch(BaseRule):
    """Verify incorporation date on PAN matches Udyam registration."""
    
    @property
    def rule_id(self) -> str:
        return "INCORPORATION_DATE_PAN_UDYAM"
    
    @property
    def description(self) -> str:
        return "Date of incorporation on PAN should match Udyam registration"
    
    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL
    
    @property
    def source_docs(self) -> List[str]:
        return ["PAN", "UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing PAN or Udyam data")
        
        pan_date = entity["pan"].get("incorporation_date", "")
        udyam_date = entity["udyam"].get("incorporation_date", "")
        
        if not pan_date:
            return self.skip_result("Incorporation date missing from PAN")
        
        if not udyam_date:
            return self.skip_result("Incorporation date missing from Udyam")
        
        if pan_date == udyam_date:
            return self.pass_result(
                f"Incorporation dates match: {pan_date}",
                {"pan_date": pan_date, "udyam_date": udyam_date}
            )
        else:
            return self.fail_result(
                "Incorporation dates do NOT match",
                {"pan_date": pan_date, "udyam_date": udyam_date}
            )


class EntityAgeCheck(BaseRule):
    """
    Determine if entity is new or existing based on incorporation date.
    New entity: incorporated within last 2 years
    """
    
    @property
    def rule_id(self) -> str:
        return "ENTITY_AGE_CHECK"
    
    @property
    def description(self) -> str:
        return "Classify entity as new (< 2 years) or existing based on incorporation date"
    
    @property
    def severity(self) -> Severity:
        return Severity.INFO
    
    @property
    def source_docs(self) -> List[str]:
        return ["UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing Udyam data")
        
        inc_date_str = entity["udyam"].get("incorporation_date", "")
        
        if not inc_date_str:
            return self.skip_result("Incorporation date not available")
        
        try:
            # Parse date (expected format: DD/MM/YYYY)
            inc_date = datetime.strptime(inc_date_str, "%d/%m/%Y")
            today = datetime.now()
            age_days = (today - inc_date).days
            age_years = age_days / 365.25
            
            entity_status = "NEW" if age_years < 2 else "EXISTING"
            
            details = {
                "incorporation_date": inc_date_str,
                "age_years": round(age_years, 1),
                "entity_status": entity_status,
                "enterprise_type": entity["udyam"].get("enterprise_type", "")
            }
            
            return self.pass_result(
                f"Entity is {entity_status} (incorporated {round(age_years, 1)} years ago)",
                details
            )
            
        except ValueError:
            return self.skip_result(f"Could not parse date: {inc_date_str}")


class CommencementDateCheck(BaseRule):
    """
    Check if incorporation and commencement dates indicate an existing entity.
    If both are same, it may indicate an existing entity that recently registered.
    """
    
    @property
    def rule_id(self) -> str:
        return "INCORPORATION_VS_COMMENCEMENT"
    
    @property
    def description(self) -> str:
        return "Compare incorporation and commencement dates to detect existing entities"
    
    @property
    def severity(self) -> Severity:
        return Severity.INFO
    
    @property
    def source_docs(self) -> List[str]:
        return ["UDYAM"]
    
    def validate(self, entity: Dict) -> RuleResult:
        if not self.has_required_data(entity):
            return self.skip_result("Missing Udyam data")
        
        inc_date = entity["udyam"].get("incorporation_date", "")
        com_date = entity["udyam"].get("commencement_date", "")
        
        if not inc_date or not com_date:
            return self.pass_result(
                "Commencement date not available for comparison",
                {"incorporation_date": inc_date, "commencement_date": com_date}
            )
        
        details = {
            "incorporation_date": inc_date,
            "commencement_date": com_date
        }
        
        if inc_date == com_date:
            return self.warning_result(
                "Incorporation and commencement dates are same - may indicate existing entity",
                details
            )
        else:
            return self.pass_result(
                "Incorporation and commencement dates differ",
                details
            )
