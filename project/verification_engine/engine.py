"""
Verification Engine - Main Orchestrator

Central engine that loads documents, applies adapters, runs all rules,
and generates verification reports.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from .adapters.pan_adapter import PANAdapter
from .adapters.gst_adapter import GSTAdapter
from .adapters.udyam_adapter import UdyamAdapter
from .rules.rule_registry import get_registry, RuleRegistry
from .rules.base_rule import RuleResult, Status, Severity
from .report_generator import ReportGenerator
from .config import VerificationConfig, get_default_output_paths


class VerificationEngine:
    """
    Main verification engine that orchestrates document verification.
    
    Usage:
        engine = VerificationEngine()
        report = engine.verify_from_files(pan_path, gst_path, udyam_path)
        print(report.to_console())
    """
    
    def __init__(self, config: Optional[VerificationConfig] = None):
        self.config = config or VerificationConfig()
        self.registry = get_registry()
        
        # Initialize adapters
        self.adapters = {
            "pan": PANAdapter(),
            "gst": GSTAdapter(),
            "udyam": UdyamAdapter()
        }
    
    def load_json(self, path: str) -> Dict:
        """Load and parse a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def build_entity(self, pan_data: Dict, gst_data: Dict, udyam_data: Dict) -> Dict:
        """
        Build a normalized entity from raw document data.
        
        Returns:
            Dict with 'pan', 'gst', 'udyam' keys containing normalized data.
        """
        entity = {}
        
        if pan_data:
            entity["pan"] = self.adapters["pan"].adapt(pan_data)
        else:
            entity["pan"] = {}
        
        if gst_data:
            entity["gst"] = self.adapters["gst"].adapt(gst_data)
        else:
            entity["gst"] = {}
        
        if udyam_data:
            entity["udyam"] = self.adapters["udyam"].adapt(udyam_data)
        else:
            entity["udyam"] = {}
        
        return entity
    
    def run_rules(self, entity: Dict) -> List[RuleResult]:
        """
        Execute all enabled rules against the entity.
        
        Returns:
            List of RuleResult objects.
        """
        results = []
        
        for rule in self.registry.get_all_rules():
            # Skip disabled rules
            if not self.config.is_rule_enabled(rule.rule_id):
                continue
            
            # Apply severity filter
            if self.config.severity_filter:
                severity_order = ["INFO", "WARNING", "CRITICAL"]
                if severity_order.index(rule.severity.value) < \
                   severity_order.index(self.config.severity_filter):
                    continue
            
            # Execute rule
            try:
                result = rule.validate(entity)
                results.append(result)
                
                # Check if we should stop on critical failure
                if (self.config.stop_on_critical_fail and 
                    result.status == Status.FAIL and 
                    result.severity == Severity.CRITICAL):
                    break
                    
            except Exception as e:
                # Create error result for failed rules
                results.append(RuleResult(
                    rule_id=rule.rule_id,
                    status=Status.SKIPPED,
                    message=f"Rule execution error: {str(e)}",
                    severity=rule.severity,
                    source_docs=rule.source_docs,
                    details={"error": str(e)}
                ))
        
        return results
    
    def verify(self, entity: Dict) -> ReportGenerator:
        """
        Run verification on a pre-built entity.
        
        Args:
            entity: Normalized entity dict with pan, gst, udyam data.
            
        Returns:
            ReportGenerator instance with results.
        """
        results = self.run_rules(entity)
        return ReportGenerator(entity, results)
    
    def verify_from_files(
        self, 
        pan_path: Optional[str] = None,
        gst_path: Optional[str] = None,
        udyam_path: Optional[str] = None
    ) -> ReportGenerator:
        """
        Load documents from files and run verification.
        
        Args:
            pan_path: Path to PAN output JSON (optional)
            gst_path: Path to GST output JSON (optional)
            udyam_path: Path to Udyam output JSON (optional)
            
        Returns:
            ReportGenerator instance with results.
        """
        pan_data = self.load_json(pan_path) if pan_path else None
        gst_data = self.load_json(gst_path) if gst_path else None
        udyam_data = self.load_json(udyam_path) if udyam_path else None
        
        entity = self.build_entity(pan_data, gst_data, udyam_data)
        return self.verify(entity)
    
    def verify_from_default_paths(self) -> ReportGenerator:
        """Load documents from default output paths and run verification."""
        paths = get_default_output_paths()
        return self.verify_from_files(
            pan_path=paths["pan"],
            gst_path=paths["gst"],
            udyam_path=paths["udyam"]
        )
    
    def get_available_rules(self) -> List[Dict]:
        """List all available rules with their metadata."""
        return [
            {
                "rule_id": r.rule_id,
                "description": r.description,
                "severity": r.severity.value,
                "source_docs": r.source_docs,
                "enabled": self.config.is_rule_enabled(r.rule_id)
            }
            for r in self.registry.get_all_rules(include_disabled=True)
        ]


def main():
    """Main entry point for running verification from command line."""
    engine = VerificationEngine()
    
    print("Loading documents from default paths...")
    report = engine.verify_from_default_paths()
    
    # Print console report
    print(report.to_console(verbose=True))
    
    # Save JSON report
    output_path = Path(__file__).parent.parent / "output" / "verification_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report.to_json())
    print(f"\nJSON report saved to: {output_path}")


if __name__ == "__main__":
    main()
