"""Data models for Phase 3: Logic Engine."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Tuple

import networkx as nx


@dataclass(frozen=True)
class Violation:
    """Represents a single architectural violation.

    Frozen to make hashable for set storage.
    """

    type: str  # DIRECT_VIOLATION, TRANSITIVE_VIOLATION, LAYER_BYPASS, etc.
    source_class: str
    target_class: str
    violation_path: Tuple[str, ...] = field(default_factory=tuple)  # Call chain (immutable)
    line_number: int = 0
    filename: str = ""
    description: Optional[str] = None
    severity: str = "high"  # high, medium, low

    def __hash__(self) -> int:
        """Make hashable for set storage."""
        return hash((self.type, self.source_class, self.target_class, self.violation_path))

    def __eq__(self, other) -> bool:
        """Compare violations."""
        if not isinstance(other, Violation):
            return False
        return (self.type == other.type and
                self.source_class == other.source_class and
                self.target_class == other.target_class and
                self.violation_path == other.violation_path)


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
            "violation_path": list(self.violation.violation_path),
            "line_number": self.violation.line_number,
            "filename": self.violation.filename,
            "description": self.violation.description,
            "severity": self.violation.severity,
            "architecture_rule": self.architecture_rule,
            "suggested_fix": self.suggested_fix,
            "call_chain_details": self.call_chain_details,
        }


@dataclass
class ViolationReport:
    """Complete violation report with summary statistics."""

    violations: Set[Violation] = field(default_factory=set)
    total_violations: int = 0
    critical_violations: int = 0
    direct_violations: int = 0
    transitive_violations: int = 0

    def add_violation(self, violation: Violation) -> None:
        """Add a violation to the report."""
        self.violations.add(violation)
        self.total_violations = len(self.violations)

        if violation.severity == "high":
            self.critical_violations += 1
        if violation.type == "DIRECT_VIOLATION":
            self.direct_violations += 1
        elif violation.type in ["TRANSITIVE_VIOLATION", "LAYER_BYPASS"]:
            self.transitive_violations += 1

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_violations": self.total_violations,
            "critical_violations": self.critical_violations,
            "direct_violations": self.direct_violations,
            "transitive_violations": self.transitive_violations,
            "violations": [
                {
                    "type": v.type,
                    "source_class": v.source_class,
                    "target_class": v.target_class,
                    "violation_path": list(v.violation_path),
                    "severity": v.severity,
                }
                for v in sorted(self.violations,
                              key=lambda x: (x.source_class, x.target_class))
            ]
        }
