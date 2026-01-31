"""
Verification Report Generator

Formats verification results for console and JSON output.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

from .rules.base_rule import RuleResult, Status, Severity


class ReportGenerator:
    """Generate formatted verification reports."""
    
    def __init__(self, entity: Dict, results: List[RuleResult]):
        self.entity = entity
        self.results = results
        self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Generate minimal report as dictionary."""
        summary = self._generate_summary()
        
        # Separate passed and failed results for minimal output
        passed_results = []
        failed_results = []
        
        for r in self.results:
            minimal_result = self._to_minimal_result(r)
            if r.status == Status.PASS:
                passed_results.append(minimal_result)
            elif r.status in (Status.FAIL, Status.WARNING):
                failed_results.append(minimal_result)
        
        return {
            "report_generated_at": self.generated_at,
            "entity_info": self._get_entity_info(),
            "summary": summary,
            "mismatches": failed_results,
            "matches": passed_results
        }
    
    def _to_minimal_result(self, r: RuleResult) -> Dict:
        """Convert a RuleResult to minimal format showing only essential info."""
        result = {
            "rule": r.rule_id,
            "status": r.status.value,
            "message": r.message
        }
        
        if r.status == Status.PASS:
            # For passes, show what matched (extract the matched value)
            result["matched"] = self._extract_matched_value(r)
        elif r.status in (Status.FAIL, Status.WARNING):
            # For failures, show the comparison
            result["comparison"] = self._extract_comparison(r)
        
        return result
    
    def _extract_matched_value(self, r: RuleResult) -> Optional[str]:
        """Extract the matched value from a passing result."""
        details = r.details
        if not details:
            return None
        
        # For name matches, return the matched name
        if "pan_name" in details and "gst_name" in details:
            return details["pan_name"]
        if "gst_name" in details and "udyam_name" in details:
            return details["gst_name"]
        if "pan_name" in details and "udyam_name" in details:
            return details["pan_name"]
        
        # For PAN matches
        if "pan" in details:
            return details["pan"]
        
        # For PIN matches
        if "gst_pin" in details and "udyam_pin" in details:
            return details["gst_pin"]
        
        # For date matches
        if "pan_date" in details and "udyam_date" in details:
            return details["pan_date"]
        
        # For constitution matches
        if "gst_constitution" in details:
            return details["gst_constitution"]
        
        # For factory matches - show matching pins
        if "matching_pins" in details:
            pins = [p.get("pin") for p in details["matching_pins"] if p.get("pin")]
            return f"Matching PINs: {', '.join(pins)}" if pins else None
        
        # Fallback - return first value found
        for key, value in details.items():
            if value and not key.endswith("_raw") and key != "skip_reason":
                return str(value) if len(str(value)) <= 50 else str(value)[:50] + "..."
        
        return None
    
    def _extract_comparison(self, r: RuleResult) -> Dict:
        """Extract comparison details for failed results."""
        details = r.details
        comparison = {}
        
        if not details:
            return comparison
        
        # For address mismatches
        if "gst_address" in details and "udyam_address" in details:
            comparison["gst"] = details["gst_address"]
            comparison["udyam"] = details["udyam_address"]
            if "matches" in details:
                comparison["matched_fields"] = details["matches"]
            if "mismatches" in details and details["mismatches"]:
                comparison["mismatched_fields"] = details["mismatches"]
            if "match_score" in details:
                comparison["score"] = details["match_score"]
        
        # For name mismatches
        elif any(k.endswith("_name") for k in details):
            names = {k: v for k, v in details.items() if k.endswith("_name") and v}
            if names:
                comparison = names
        
        # For PAN mismatches
        elif "pan" in details:
            comparison = {k: v for k, v in details.items() if "pan" in k.lower()}
        
        # For date mismatches
        elif any(k.endswith("_date") for k in details):
            comparison = {k: v for k, v in details.items() if k.endswith("_date")}
        
        # Fallback - include all details
        else:
            comparison = {k: v for k, v in details.items() 
                         if v and k != "skip_reason" and not k.endswith("_raw")}
        
        return comparison
    
    def to_json(self, indent: int = 2) -> str:
        """Generate JSON string report."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_console(self, verbose: bool = True) -> str:
        """Generate console-friendly report."""
        lines = []
        summary = self._generate_summary()
        
        lines.append("=" * 60)
        lines.append("DOCUMENT VERIFICATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {self.generated_at}")
        lines.append("")
        
        # Entity info
        entity_info = self._get_entity_info()
        lines.append("Entity Information:")
        lines.append(f"  Name: {entity_info.get('name', 'N/A')}")
        lines.append(f"  PAN: {entity_info.get('pan', 'N/A')}")
        lines.append(f"  GST: {entity_info.get('gst_number', 'N/A')}")
        lines.append(f"  Udyam: {entity_info.get('udyam_number', 'N/A')}")
        lines.append("")
        
        # Summary
        lines.append("-" * 60)
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(f"  Total Rules: {summary['total_rules']}")
        lines.append(f"  [PASS] Passed: {summary['passed']} ({summary['pass_rate']})")
        lines.append(f"  [FAIL] Failed: {summary['failed']}")
        lines.append(f"  [WARN] Warning: {summary['warnings']}")
        lines.append(f"  [SKIP] Skipped: {summary['skipped']}")
        lines.append(f"  Overall: {summary['overall_status']}")
        lines.append("")
        
        # Critical failures
        critical_fails = [r for r in self.results 
                        if r.severity == Severity.CRITICAL and r.status == Status.FAIL]
        if critical_fails:
            lines.append("-" * 60)
            lines.append("⛔ CRITICAL FAILURES")
            lines.append("-" * 60)
            for r in critical_fails:
                lines.append(f"  [{r.rule_id}]")
                lines.append(f"    {r.message}")
                if verbose and r.details:
                    for k, v in r.details.items():
                        lines.append(f"    • {k}: {v}")
            lines.append("")
        
        # All results
        lines.append("-" * 60)
        lines.append("DETAILED RESULTS")
        lines.append("-" * 60)
        
        # Group by status
        for status in [Status.FAIL, Status.WARNING, Status.PASS, Status.SKIPPED]:
            status_results = [r for r in self.results if r.status == status]
            if status_results:
                icon = {"PASS": "[+]", "FAIL": "[x]", "WARNING": "[!]", "SKIPPED": "[o]"}[status.value]
                lines.append(f"\n  {icon} {status.value} ({len(status_results)})")
                lines.append("  " + "-" * 40)
                for r in status_results:
                    severity_tag = f"[{r.severity.value}]"
                    lines.append(f"    {r.rule_id} {severity_tag}")
                    lines.append(f"      -> {r.message}")
                    if verbose and r.details and status != Status.SKIPPED:
                        for k, v in r.details.items():
                            if k != "skip_reason":
                                val_str = str(v)[:80] + "..." if len(str(v)) > 80 else str(v)
                                lines.append(f"        {k}: {val_str}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        passed = sum(1 for r in self.results if r.status == Status.PASS)
        failed = sum(1 for r in self.results if r.status == Status.FAIL)
        warnings = sum(1 for r in self.results if r.status == Status.WARNING)
        skipped = sum(1 for r in self.results if r.status == Status.SKIPPED)
        total = len(self.results)
        
        critical_fails = sum(1 for r in self.results 
                           if r.status == Status.FAIL and r.severity == Severity.CRITICAL)
        
        if critical_fails > 0:
            overall = "FAILED (Critical issues found)"
        elif failed > 0:
            overall = "FAILED"
        elif warnings > 0:
            overall = "PASSED WITH WARNINGS"
        else:
            overall = "PASSED"
        
        return {
            "total_rules": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "critical_failures": critical_fails,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A",
            "overall_status": overall
        }
    
    def _get_entity_info(self) -> Dict:
        """Extract key entity information for report header."""
        pan_data = self.entity.get("pan", {})
        gst_data = self.entity.get("gst", {})
        udyam_data = self.entity.get("udyam", {})
        
        return {
            "name": pan_data.get("raw_name") or gst_data.get("raw_name") or udyam_data.get("raw_name", "N/A"),
            "pan": pan_data.get("pan", "N/A"),
            "gst_number": gst_data.get("gst_number", "N/A"),
            "udyam_number": udyam_data.get("udyam_number", "N/A"),
            "incorporation_date": udyam_data.get("incorporation_date", "N/A")
        }
    

