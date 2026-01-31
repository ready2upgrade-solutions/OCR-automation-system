"""
Base Rule Interface for Document Verification

All verification rules must inherit from BaseRule and implement the validate() method.
This provides a consistent interface for the rule registry and verification engine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class Severity(Enum):
    """Rule severity levels for prioritizing verification results."""
    CRITICAL = "CRITICAL"  # Must pass for valid verification
    WARNING = "WARNING"    # Should be reviewed but not blocking
    INFO = "INFO"          # Informational only


class Status(Enum):
    """Verification result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"    # Rule skipped due to missing data


@dataclass
class RuleResult:
    """
    Result of a single rule validation.
    
    Attributes:
        rule_id: Unique identifier for the rule
        status: PASS, FAIL, WARNING, or SKIPPED
        message: Human-readable result description
        details: Additional context (field values compared, scores, etc.)
        severity: Rule severity level
        source_docs: Documents involved in this check
    """
    rule_id: str
    status: Status
    message: str
    severity: Severity
    source_docs: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "rule_id": self.rule_id,
            "status": self.status.value,
            "message": self.message,
            "severity": self.severity.value,
            "source_docs": self.source_docs,
            "details": self.details
        }


class BaseRule(ABC):
    """
    Abstract base class for all verification rules.
    
    Subclasses must implement:
        - rule_id: Unique identifier string
        - description: Human-readable rule description
        - severity: Severity level (CRITICAL, WARNING, INFO)
        - source_docs: List of document types this rule validates
        - validate(): Core validation logic
    """
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule (e.g., 'NAME_MATCH_PAN_GST')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this rule validates."""
        pass
    
    @property
    @abstractmethod
    def severity(self) -> Severity:
        """Severity level of this rule."""
        pass
    
    @property
    @abstractmethod
    def source_docs(self) -> List[str]:
        """List of document types this rule applies to (e.g., ['PAN', 'GST'])."""
        pass
    
    @abstractmethod
    def validate(self, entity: Dict) -> RuleResult:
        """
        Execute the validation logic.
        
        Args:
            entity: Normalized entity containing all document data.
                    Expected structure: {
                        "pan": {...normalized PAN data...},
                        "gst": {...normalized GST data...},
                        "udyam": {...normalized Udyam data...}
                    }
        
        Returns:
            RuleResult with status, message, and details.
        """
        pass
    
    def has_required_data(self, entity: Dict) -> bool:
        """
        Check if entity has data from all required source documents.
        Override in subclasses for custom data availability checks.
        """
        for doc in self.source_docs:
            doc_key = doc.lower()
            if doc_key not in entity or not entity[doc_key]:
                return False
        return True
    
    def skip_result(self, reason: str) -> RuleResult:
        """Create a SKIPPED result when required data is missing."""
        return RuleResult(
            rule_id=self.rule_id,
            status=Status.SKIPPED,
            message=f"Skipped: {reason}",
            severity=self.severity,
            source_docs=self.source_docs,
            details={"skip_reason": reason}
        )
    
    def pass_result(self, message: str, details: Optional[Dict] = None) -> RuleResult:
        """Create a PASS result."""
        return RuleResult(
            rule_id=self.rule_id,
            status=Status.PASS,
            message=message,
            severity=self.severity,
            source_docs=self.source_docs,
            details=details or {}
        )
    
    def fail_result(self, message: str, details: Optional[Dict] = None) -> RuleResult:
        """Create a FAIL result."""
        return RuleResult(
            rule_id=self.rule_id,
            status=Status.FAIL,
            message=message,
            severity=self.severity,
            source_docs=self.source_docs,
            details=details or {}
        )
    
    def warning_result(self, message: str, details: Optional[Dict] = None) -> RuleResult:
        """Create a WARNING result."""
        return RuleResult(
            rule_id=self.rule_id,
            status=Status.WARNING,
            message=message,
            severity=self.severity,
            source_docs=self.source_docs,
            details=details or {}
        )
