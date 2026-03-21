"""Data models for Phase 3: Logic Engine."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import networkx as nx


@dataclass
class Violation:
    """Represents a single architectural violation."""

    type: str  # DIRECT_VIOLATION, TRANSITIVE_VIOLATION, LAYER_BYPASS, etc.
    source_class: str
    target_class: str
    violation_path: List[str] = field(default_factory=list)  # Call chain
    line_number: int = 0
    filename: str = ""
    description: Optional[str] = None
    severity: str = "high"  # high, medium, low


@dataclass
class ViolationTrace:
    """Complete trace of a violation including context."""

    violation: Violation
    architecture_rule: Optional[str] = None
    suggested_fix: Optional[str] = None
    call_chain_details: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "type": self.violation.type,
            "source_class": self.violation.source_class,
            "target_class": self.violation.target_class,
            "violation_path": self.violation.violation_path,
            "line_number": self.violation.line_number,
            "filename": self.violation.filename,
            "description": self.violation.description,
            "severity": self.violation.severity,
            "architecture_rule": self.architecture_rule,
            "suggested_fix": self.suggested_fix,
        }
