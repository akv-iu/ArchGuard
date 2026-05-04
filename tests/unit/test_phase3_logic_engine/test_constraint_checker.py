"""Unit tests for Phase 3 constraint checker."""

import pytest

from archguard.phase1_symbolic_brain.models import (
    ArchitectureEdge,
    ArchitectureClass,
    ArchitectureEdge,
    ArchitectureGraph,
)
from archguard.phase2_code_abstraction.models import (
    MethodCall,
    ImplementationGraph,
    ClassDefinition,
)
from archguard.phase3_logic_engine.constraint_checker import ConstraintChecker
from archguard.phase3_logic_engine.models import Violation


class TestConstraintChecker:
    """Tests for ConstraintChecker."""

    def test_checker_initialization(self):
        """Test initializing constraint checker."""
        arch_graph = ArchitectureGraph()
        code_graph = ImplementationGraph()

        checker = ConstraintChecker(arch_graph, code_graph)

        assert checker.architecture_graph == arch_graph
        assert checker.code_graph == code_graph

    def test_find_violations_empty_graphs(self):
        """Test finding violations in empty graphs."""
        arch_graph = ArchitectureGraph()
        code_graph = ImplementationGraph()

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_violations()

        assert len(violations) == 0

    def test_find_direct_violation(self):
        """Test detecting a direct violation."""
        # Create architecture: A can call B
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        edge = ArchitectureEdge("A", "B", "calls")
        arch_graph.add_edge(edge)

        # Create code that violates: A calls C directly (not allowed)
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))
        code_graph.add_class(ClassDefinition("C", "file.py", 20))

        call = MethodCall(
            source_class="A",
            target_class="C",
            source_method="method1",
            target_method="method2"
        )
        code_graph.add_call(call)

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_violations()

        # Should detect violation: A calling C when architecture doesn't allow it
        assert len(violations) > 0
        assert any(v.type == "DIRECT_VIOLATION" for v in violations)

    def test_allowed_call_not_flagged(self):
        """Test that allowed calls are not flagged."""
        # Create architecture: A can call B
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        edge = ArchitectureEdge("A", "B", "calls")
        arch_graph.add_edge(edge)

        # Create code that follows architecture
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))

        call = MethodCall(
            source_class="A",
            target_class="B",
            source_method="method1",
            target_method="method2"
        )
        code_graph.add_call(call)

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_violations()

        # No violations since the call is allowed
        assert len(violations) == 0

    def test_is_call_allowed_direct_edge(self):
        """Test checking if a call is allowed (direct edge)."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        arch_graph.add_edge(ArchitectureEdge("A", "B", "calls"))

        code_graph = ImplementationGraph()
        checker = ConstraintChecker(arch_graph, code_graph)

        # Direct edge should be allowed
        assert checker._is_call_allowed("A", "B") is True

    def test_is_call_allowed_no_edge(self):
        """Test checking if a call is allowed (no edge)."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))

        code_graph = ImplementationGraph()
        checker = ConstraintChecker(arch_graph, code_graph)

        # No edge should not be allowed
        assert checker._is_call_allowed("A", "B") is False

    def test_is_call_allowed_transitive_path(self):
        """Test that a transitive architecture path does NOT make a direct call allowed.

        Arch has A→B→C but no direct A→C edge. A calling C directly is a layer
        bypass and must be flagged, not silently approved via has_path.
        """
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        arch_graph.add_class(ArchitectureClass("C", "layer3"))
        arch_graph.add_edge(ArchitectureEdge("A", "B", "calls"))
        arch_graph.add_edge(ArchitectureEdge("B", "C", "calls"))

        code_graph = ImplementationGraph()
        checker = ConstraintChecker(arch_graph, code_graph)

        # Only a direct arch edge constitutes permission — transitive path does not
        assert checker._is_call_allowed("A", "C") is False

    def test_layer_bypass_is_direct_violation(self):
        """Test that a layer-bypass call is detected as a DIRECT_VIOLATION.

        Architecture: View → Service → Repository (no View→Repository edge).
        Code: View calls Repository directly.
        Expected: DIRECT_VIOLATION reported for (View, Repository).
        """
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("View", "ui"))
        arch_graph.add_class(ArchitectureClass("Service", "service"))
        arch_graph.add_class(ArchitectureClass("Repository", "data"))
        arch_graph.add_edge(ArchitectureEdge("View", "Service", "calls"))
        arch_graph.add_edge(ArchitectureEdge("Service", "Repository", "calls"))

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("View", "view.py", 1))
        code_graph.add_class(ClassDefinition("Repository", "repo.py", 5))
        code_graph.add_call(MethodCall(
            source_class="View",
            target_class="Repository",
            source_method="render",
            target_method="find_all",
        ))

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_violations()

        assert len(violations) == 1
        v = list(violations)[0]
        assert v.type == "DIRECT_VIOLATION"
        assert v.source_class == "View"
        assert v.target_class == "Repository"

    def test_find_circular_violations_detected(self):
        """Test that a circular dependency in code is detected."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "a.py", 1))
        code_graph.add_class(ClassDefinition("B", "b.py", 1))
        # A → B → A forms a cycle
        code_graph.add_call(MethodCall(source_class="A", target_class="B", source_method="m1", target_method="m2"))
        code_graph.add_call(MethodCall(source_class="B", target_class="A", source_method="m2", target_method="m1"))

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_circular_violations()

        assert len(violations) > 0
        assert all(v.type == "CIRCULAR_DEPENDENCY" for v in violations)
        assert all(v.severity == "critical" for v in violations)

    def test_find_circular_violations_none(self):
        """Test that an acyclic code graph produces no circular violations."""
        arch_graph = ArchitectureGraph()
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "a.py", 1))
        code_graph.add_class(ClassDefinition("B", "b.py", 1))
        code_graph.add_call(MethodCall(source_class="A", target_class="B", source_method="m1", target_method="m2"))

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_circular_violations()

        assert len(violations) == 0

    def test_find_transitive_violations(self):
        """Test detecting transitive violations."""
        # Architecture: A → B, B cannot call C
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        arch_graph.add_class(ArchitectureClass("C", "layer3"))
        arch_graph.add_edge(ArchitectureEdge("A", "B", "calls"))

        # Code: A → B → C (violates architecture)
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))
        code_graph.add_class(ClassDefinition("C", "file.py", 20))

        call1 = MethodCall(
            source_class="A",
            target_class="B",
            source_method="m1",
            target_method="m2"
        )
        call2 = MethodCall(
            source_class="B",
            target_class="C",
            source_method="m2",
            target_method="m3"
        )
        code_graph.add_call(call1)
        code_graph.add_call(call2)

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_transitive_violations()

        # Should detect that A transitively reaches C (not allowed)
        assert len(violations) > 0

    def test_violation_includes_metadata(self):
        """Test that violations include proper metadata."""
        arch_graph = ArchitectureGraph()
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "test.py", 1))
        code_graph.add_class(ClassDefinition("B", "test.py", 10))

        call = MethodCall(
            source_class="A",
            target_class="B",
            source_method="method1",
            target_method="method2",
            line_number=42
        )
        code_graph.add_call(call)

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_violations()

        # Verify violation has metadata
        if violations:
            v = list(violations)[0]
            assert v.source_class == "A"
            assert v.target_class == "B"
            assert v.type in ["DIRECT_VIOLATION", "TRANSITIVE_VIOLATION"]

    def test_multiple_violations_detected(self):
        """Test detecting multiple violations."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        # No edges - no calls allowed

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))
        code_graph.add_class(ClassDefinition("C", "file.py", 20))

        # Add multiple violating calls
        code_graph.add_call(MethodCall(source_class="A", source_method="m1", target_class="B", target_method="m2"))
        code_graph.add_call(MethodCall(source_class="A", source_method="m1", target_class="C", target_method="m3"))
        code_graph.add_call(MethodCall(source_class="B", source_method="m2", target_class="C", target_method="m3"))

        checker = ConstraintChecker(arch_graph, code_graph)
        violations = checker.find_violations()

        # Should detect all three violations
        assert len(violations) == 3
