"""
Verification Engine Configuration

Centralized configuration for the verification system.
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


@dataclass
class VerificationConfig:
    """
    Configuration for the verification engine.
    
    Attributes:
        disabled_rules: Set of rule IDs to skip
        severity_filter: Only run rules at or above this severity
        stop_on_critical_fail: Stop verification if a CRITICAL rule fails
        output_format: 'json', 'console', or 'both'
        verbose: Include detailed field comparisons in output
    """
    
    disabled_rules: Set[str] = field(default_factory=set)
    severity_filter: Optional[str] = None  # 'CRITICAL', 'WARNING', 'INFO' or None for all
    stop_on_critical_fail: bool = False
    output_format: str = "both"  # 'json', 'console', 'both'
    verbose: bool = True
    
    # Document paths (can be set programmatically)
    pan_path: Optional[str] = None
    gst_path: Optional[str] = None
    udyam_path: Optional[str] = None
    
    def disable_rule(self, rule_id: str) -> None:
        """Add a rule to the disabled set."""
        self.disabled_rules.add(rule_id)
    
    def enable_rule(self, rule_id: str) -> None:
        """Remove a rule from the disabled set."""
        self.disabled_rules.discard(rule_id)
    
    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled."""
        return rule_id not in self.disabled_rules


# Default configuration
DEFAULT_CONFIG = VerificationConfig()


def get_default_output_paths() -> Dict[str, str]:
    """Get default paths to output JSON files."""
    base_path = r"C:\Users\Tirth\OneDrive\Documents\codes\ocr\OCR-automation-system\project\output"
    return {
        "pan": f"{base_path}\\pan_output.json",
        "gst": f"{base_path}\\gst_output.json",
        "udyam": f"{base_path}\\udyam_output.json"
    }
