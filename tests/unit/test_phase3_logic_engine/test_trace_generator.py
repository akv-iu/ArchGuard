"""Unit tests for Phase 3 trace generator."""

import json
import pytest

from archguard.phase3_logic_engine.models import Violation, ViolationTrace, ViolationReport
from archguard.phase3_logic_engine.trace_generator import TraceGenerator


class TestTraceGenerator:
    """Tests for TraceGenerator."""

    def test_generate_json_traces_empty(self):
        """Test generating JSON traces from empty violations."""
        violations = set()

        json_output = TraceGenerator.generate_json_traces(violations)
        data = json.loads(json_output)

        assert data["total_violations"] == 0
        assert len(data["violations"]) == 0

    def test_generate_json_traces_single_violation(self):
        """Test generating JSON traces from single violation."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B",
            severity="high"
        )
        violations = {v}

        json_output = TraceGenerator.generate_json_traces(violations)
        data = json.loads(json_output)

        assert data["total_violations"] == 1
        assert data["violations"][0]["type"] == "DIRECT_VIOLATION"
        assert data["violations"][0]["source_class"] == "A"

    def test_generate_json_traces_multiple(self):
        """Test generating JSON traces from multiple violations."""
        v1 = Violation("DIRECT_VIOLATION", "A", "B")
        v2 = Violation("TRANSITIVE_VIOLATION", "C", "D")
        violations = {v1, v2}

        json_output = TraceGenerator.generate_json_traces(violations)
        data = json.loads(json_output)

        assert data["total_violations"] == 2

    def test_generate_json_traces_valid_json(self):
        """Test that generated output is valid JSON."""
        v = Violation("DIRECT_VIOLATION", "A", "B")
        violations = {v}

        json_output = TraceGenerator.generate_json_traces(violations)

        # Should not raise
        data = json.loads(json_output)
        assert isinstance(data, dict)

    def test_generate_violation_traces(self):
        """Test generating violation traces with context."""
        v = Violation("DIRECT_VIOLATION", "A", "B")
        violations = {v}

        traces = TraceGenerator.generate_violation_traces(violations)

        assert len(traces) == 1
        assert traces[0].violation == v

    def test_generate_violation_traces_with_suggestions(self):
        """Test that violation traces include fix suggestions."""
        v = Violation("DIRECT_VIOLATION", "A", "B")
        violations = {v}

        traces = TraceGenerator.generate_violation_traces(violations)

        assert traces[0].suggested_fix is not None
        assert "Remove" in traces[0].suggested_fix or "remove" in traces[0].suggested_fix

    def test_suggest_fix_direct_violation(self):
        """Test fix suggestion for direct violations."""
        v = Violation("DIRECT_VIOLATION", "View", "Repository")

        fix = TraceGenerator._suggest_fix(v)

        assert "View" in fix
        assert "Repository" in fix
        assert "Remove" in fix or "remove" in fix

    def test_suggest_fix_transitive_violation(self):
        """Test fix suggestion for transitive violations."""
        v = Violation("TRANSITIVE_VIOLATION", "A", "B")

        fix = TraceGenerator._suggest_fix(v)

        assert "Break" in fix or "break" in fix or len(fix) > 0

    def test_get_architecture_rule_exists(self):
        """Test getting architecture rule when path exists."""
        from archguard.phase1_symbolic_brain.models import ArchitectureClass, ArchitectureEdge, ArchitectureGraph

        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        arch_graph.add_edge(ArchitectureEdge("A", "B", "calls"))

        rule = TraceGenerator._get_architecture_rule("A", "B", arch_graph)

        assert "allows" in rule.lower()

    def test_get_architecture_rule_not_exists(self):
        """Test getting architecture rule when path doesn't exist."""
        from archguard.phase1_symbolic_brain.models import ArchitectureClass, ArchitectureGraph

        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        # No edge

        rule = TraceGenerator._get_architecture_rule("A", "B", arch_graph)

        assert "not" in rule.lower() or "does" in rule.lower()

    def test_generate_human_readable_empty(self):
        """Test generating human-readable report with no violations."""
        violations = set()

        report = TraceGenerator.generate_human_readable(violations)

        assert "✅" in report or "No" in report

    def test_generate_human_readable_single(self):
        """Test generating human-readable report with single violation."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="View",
            target_class="Repository",
            severity="high"
        )
        violations = {v}

        report = TraceGenerator.generate_human_readable(violations)

        assert "View" in report
        assert "Repository" in report
        assert "DIRECT_VIOLATION" in report

    def test_generate_human_readable_multiple(self):
        """Test generating human-readable report with multiple violations."""
        v1 = Violation("DIRECT_VIOLATION", "A", "B", severity="high")
        v2 = Violation("TRANSITIVE_VIOLATION", "C", "D", severity="medium")
        violations = {v1, v2}

        report = TraceGenerator.generate_human_readable(violations)

        assert "Violation #1" in report or "Violation" in report
        assert "A" in report
        assert "C" in report

    def test_generate_human_readable_max_violations(self):
        """Test limiting human-readable report output."""
        violations = {
            Violation("DIRECT_VIOLATION", f"A{i}", f"B{i}") for i in range(10)
        }

        report = TraceGenerator.generate_human_readable(violations, max_violations=3)

        # Should only list first 3
        assert report.count("Violation #") <= 3

    def test_generate_human_readable_formatting(self):
        """Test human-readable report formatting."""
        v = Violation(
            type="DIRECT_VIOLATION",
            source_class="A",
            target_class="B",
            severity="high",
            violation_path=("A → B",)
        )
        violations = {v}

        report = TraceGenerator.generate_human_readable(violations)

        # Should have typical report structure
        assert ":" in report  # Key-value pairs
        assert "-" in report or "=" in report  # Visual separators

    def test_violation_trace_to_dict_complete(self):
        """Test complete trace-to-dict conversion."""
        v = Violation(
            type="TRANSITIVE_VIOLATION",
            source_class="A",
            target_class="C",
            violation_path=("A → B → C",),
            line_number=42,
            filename="test.py"
        )
        trace = ViolationTrace(
            violation=v,
            architecture_rule="A should not reach C",
            suggested_fix="Refactor",
            call_chain_details={"hops": 2}
        )

        trace_dict = trace.to_dict()

        assert trace_dict["type"] == "TRANSITIVE_VIOLATION"
        assert trace_dict["line_number"] == 42
        assert trace_dict["filename"] == "test.py"
        assert trace_dict["architecture_rule"] == "A should not reach C"
        assert trace_dict["suggested_fix"] == "Refactor"
