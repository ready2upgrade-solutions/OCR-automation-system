"""
Rule Registry for Dynamic Rule Discovery and Management

Provides automatic rule discovery from the rules package and filtering capabilities.
"""

import importlib
import pkgutil
from typing import Dict, List, Optional, Type, Set
from .base_rule import BaseRule, RuleResult


class RuleRegistry:
    """
    Central registry for all verification rules.
    
    Features:
        - Automatic discovery of rule classes from rules package
        - Filtering by document type
        - Enable/disable rules dynamically
        - Rule grouping and categorization
    """
    
    def __init__(self):
        self._rules: Dict[str, BaseRule] = {}
        self._disabled_rules: Set[str] = set()
    
    def register(self, rule: BaseRule) -> None:
        """Register a rule instance."""
        self._rules[rule.rule_id] = rule
    
    def unregister(self, rule_id: str) -> None:
        """Remove a rule from registry."""
        self._rules.pop(rule_id, None)
    
    def disable(self, rule_id: str) -> None:
        """Disable a rule without removing it."""
        self._disabled_rules.add(rule_id)
    
    def enable(self, rule_id: str) -> None:
        """Re-enable a disabled rule."""
        self._disabled_rules.discard(rule_id)
    
    def is_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled."""
        return rule_id not in self._disabled_rules
    
    def get_rule(self, rule_id: str) -> Optional[BaseRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)
    
    def get_all_rules(self, include_disabled: bool = False) -> List[BaseRule]:
        """Get all registered rules, optionally including disabled ones."""
        if include_disabled:
            return list(self._rules.values())
        return [r for r in self._rules.values() if self.is_enabled(r.rule_id)]
    
    def get_rules_for_docs(self, doc_types: List[str]) -> List[BaseRule]:
        """
        Get rules that apply to the given document types.
        
        Args:
            doc_types: List of document types (e.g., ['PAN', 'GST'])
        
        Returns:
            Rules where all source_docs are in doc_types
        """
        doc_set = {d.upper() for d in doc_types}
        return [
            r for r in self.get_all_rules()
            if all(d.upper() in doc_set for d in r.source_docs)
        ]
    
    def get_rules_by_severity(self, severity: str) -> List[BaseRule]:
        """Get all rules with the specified severity."""
        return [
            r for r in self.get_all_rules()
            if r.severity.value == severity.upper()
        ]
    
    def discover_rules(self, package_name: str = "verification_engine.rules") -> int:
        """
        Auto-discover and register all rule classes from the rules package.
        
        Args:
            package_name: Name of the package to scan for rule modules
        
        Returns:
            Number of rules discovered and registered
        """
        count = 0
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            return 0
        
        # Iterate through all modules in the package
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            if modname.startswith("_") or modname == "base_rule" or modname == "rule_registry":
                continue
            
            try:
                module = importlib.import_module(f"{package_name}.{modname}")
            except ImportError:
                continue
            
            # Find all BaseRule subclasses in the module
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseRule) and 
                    obj is not BaseRule):
                    try:
                        rule_instance = obj()
                        self.register(rule_instance)
                        count += 1
                    except Exception:
                        pass  # Skip rules that can't be instantiated
        
        return count
    
    def __len__(self) -> int:
        return len(self._rules)
    
    def __iter__(self):
        return iter(self.get_all_rules())


# Global registry instance
_global_registry: Optional[RuleRegistry] = None


def get_registry() -> RuleRegistry:
    """Get the global rule registry, creating if needed."""
    global _global_registry
    if _global_registry is None:
        _global_registry = RuleRegistry()
        _global_registry.discover_rules()
    return _global_registry


def reset_registry() -> None:
    """Reset the global registry (mainly for testing)."""
    global _global_registry
    _global_registry = None
