"""Unit tests for Phase 3 models."""

import pytest

from archguard.phase3_logic_engine.models import Violation, ViolationTrace, ViolationReport


class TestViolation:
    """Tests for Violation model."""

    def test_violation_initialization(self):
        """Test creating a violation."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="View",
            target_class="Repository"
        )

        assert v.type == "DIRECT_VIOLATION"
        assert v.source_class == "View"
        assert v.target_class == "Repository"
        assert v.severity == "high"

    def test_violation_with_path(self):
        """Test violation with violation path."""
        v = Violation(
            type="TRANSITIVE_VIOLATION",
            source_class="View",
            target_class="Database",
            violation_path=("View → Service → Repository → Database",)
        )

        assert len(v.violation_path) == 1
        assert "View" in v.violation_path[0]

    def test_violation_hashable(self):
        """Test that violations are hashable."""
        v1 = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )
        v2 = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )

        # Should be able to add to set
        violation_set = {v1, v2}
        assert len(violation_set) == 1  # Duplicates collapsed

    def test_violation_equality(self):
        """Test violation equality."""
        v1 = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )
        v2 = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )
        v3 = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="C"
        )

        assert v1 == v2
        assert v1 != v3

    def test_violation_immutable(self):
        """Test that violations are immutable (frozen)."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )

        with pytest.raises(AttributeError):
            v.source_class = "C"

    def test_violation_different_severities(self):
        """Test violations with different severities."""
        v_high = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B",
            severity="high"
        )
        v_medium = Violation(
            type="TRANSITIVE_VIOLATION",
            source_class="A",
            target_class="B",
            severity="medium"
        )

        assert v_high.severity == "high"
        assert v_medium.severity == "medium"


class TestViolationTrace:
    """Tests for ViolationTrace model."""

    def test_trace_initialization(self):
        """Test creating a violation trace."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )
        trace = ViolationTrace(
            violation=v,
            architecture_rule="A should not call B",
            suggested_fix="Remove the call from A to B"
        )

        assert trace.violation == v
        assert trace.architecture_rule == "A should not call B"
        assert trace.suggested_fix == "Remove the call from A to B"

    def test_trace_to_dict(self):
        """Test converting trace to dictionary."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B",
            line_number=42
        )
        trace = ViolationTrace(violation=v)

        trace_dict = trace.to_dict()

        assert trace_dict["type"] == "DIRECT_VIOLATION"
        assert trace_dict["source_class"] == "A"
        assert trace_dict["target_class"] == "B"
        assert trace_dict["line_number"] == 42

    def test_trace_with_call_chain_details(self):
        """Test trace with call chain details."""
        v = Violation(
            type="TRANSITIVE_VIOLATION",
            source_class="View",
            target_class="Database"
        )
        details = {
            "chain": ["View", "Service", "Repository", "Database"],
            "hop_count": 3
        }
        trace = ViolationTrace(violation=v, call_chain_details=details)

        assert trace.call_chain_details["hop_count"] == 3


class TestViolationReport:
    """Tests for ViolationReport model."""

    def test_report_initialization(self):
        """Test creating a violation report."""
        report = ViolationReport()

        assert report.total_violations == 0
        assert report.critical_violations == 0
        assert len(report.violations) == 0

    def test_report_add_violation(self):
        """Test adding violations to report."""
        report = ViolationReport()
        v1 = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B",
            severity="high"
        )
        v2 = Violation(
            type="TRANSITIVE_VIOLATION",
            source_class="C",
            target_class="D",
            severity="medium"
        )

        report.add_violation(v1)
        report.add_violation(v2)

        assert report.total_violations == 2
        assert report.critical_violations == 1
        assert report.direct_violations == 1
        assert report.transitive_violations == 1

    def test_report_prevents_duplicates(self):
        """Test that report prevents duplicate violations."""
        report = ViolationReport()
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B"
        )

        report.add_violation(v)
        report.add_violation(v)  # Add the same violation again

        # Count should remain 1
        assert report.total_violations == 1
        assert len(report.violations) == 1

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        report = ViolationReport()
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B",
            severity="high"
        )
        report.add_violation(v)

        report_dict = report.to_dict()

        assert report_dict["total_violations"] == 1
        assert report_dict["critical_violations"] == 1
        assert len(report_dict["violations"]) == 1

    def test_report_statistics(self):
        """Test violation statistics in report."""
        report = ViolationReport()

        # Add different violation types and severities
        for i in range(3):
            v = Violation(
                type="DIRECT_VIOLATION",
                source_class=f"A{i}",
                target_class=f"B{i}",
                severity="high"
            )
            report.add_violation(v)

        for i in range(2):
            v = Violation(
                type="TRANSITIVE_VIOLATION",
                source_class=f"C{i}",
                target_class=f"D{i}",
                severity="medium"
            )
            report.add_violation(v)

        assert report.total_violations == 5
        assert report.critical_violations == 3
        assert report.direct_violations == 3
        assert report.transitive_violations == 2
