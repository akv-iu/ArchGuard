"""Unit tests for Phase 3 violation detector."""

import pytest

from archguard.phase1_symbolic_brain.models import (
    ArchitectureClass, ArchitectureEdge,
    ArchitectureGraph,
)
from archguard.phase2_code_abstraction.models import (
    ClassDefinition,
    ImplementationGraph,
    MethodCall,
)
from archguard.phase3_logic_engine.violation_detector import ViolationDetector


class TestViolationDetector:
    """Tests for ViolationDetector."""

    def test_detect_no_violations(self):
        """Test detecting violations when there are none."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        arch_graph.add_edge(ArchitectureEdge("A", "B", "calls"))

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))
        code_graph.add_call(MethodCall(source_class="A", source_method="m1", target_class="B", target_method="m2"))

        violations = ViolationDetector.detect(arch_graph, code_graph)

        assert len(violations) == 0

    def test_detect_direct_violations(self):
        """Test detecting direct violations."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        # No edge - A cannot call B

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))
        code_graph.add_call(MethodCall("A", "B", "m1", "m2"))

        violations = ViolationDetector.detect(arch_graph, code_graph)

        assert len(violations) > 0
        assert any(v.type == "DIRECT_VIOLATION" for v in violations)

    def test_detect_transitive_violations(self):
        """Test detecting transitive violations."""
        # Architecture: A → B only
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))
        arch_graph.add_class(ArchitectureClass("C", "layer3"))
        arch_graph.add_edge(ArchitectureEdge("A", "B", "calls"))

        # Code: A → B, B → C (transitive: A → C)
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "file.py", 1))
        code_graph.add_class(ClassDefinition("B", "file.py", 10))
        code_graph.add_class(ClassDefinition("C", "file.py", 20))
        code_graph.add_call(MethodCall("A", "B", "m1", "m2"))
        code_graph.add_call(MethodCall("B", "C", "m2", "m3"))

        violations = ViolationDetector.detect(arch_graph, code_graph)

        # Should detect transitive violation
        assert len(violations) > 0

    def test_detect_returns_set(self):
        """Test that detect returns a set."""
        arch_graph = ArchitectureGraph()
        code_graph = ImplementationGraph()

        violations = ViolationDetector.detect(arch_graph, code_graph)

        assert isinstance(violations, set)

    def test_classify_violations_by_type(self):
        """Test classifying violations by type."""
        from archguard.phase3_logic_engine.models import Violation

        v1 = Violation("DIRECT_VIOLATION", "A", "B", severity="high")
        v2 = Violation("DIRECT_VIOLATION", "C", "D", severity="high")
        v3 = Violation("TRANSITIVE_VIOLATION", "E", "F", severity="medium")

        violations = {v1, v2, v3}
        classification = ViolationDetector.classify_violations(violations)

        assert len(classification["direct"]) == 2
        assert len(classification["transitive"]) == 1

    def test_classify_violations_by_severity(self):
        """Test classifying violations by severity."""
        from archguard.phase3_logic_engine.models import Violation

        v_critical = Violation("CIRCULAR_DEPENDENCY", "A", "A", severity="critical")
        v_high = Violation("DIRECT_VIOLATION", "A", "B", severity="high")
        v_medium = Violation("TRANSITIVE_VIOLATION", "C", "D", severity="medium")
        v_low = Violation("TRANSITIVE_VIOLATION", "E", "F", severity="low")

        violations = {v_critical, v_high, v_medium, v_low}
        classification = ViolationDetector.classify_violations(violations)

        assert len(classification["critical"]) == 1
        assert len(classification["high"]) == 1
        assert len(classification["medium"]) == 1
        assert len(classification["low"]) == 1

    def test_detect_circular_violations(self):
        """Test that circular dependencies in code are detected."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("A", "layer1"))
        arch_graph.add_class(ArchitectureClass("B", "layer2"))

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("A", "a.py", 1))
        code_graph.add_class(ClassDefinition("B", "b.py", 1))
        code_graph.add_call(MethodCall(source_class="A", target_class="B", source_method="m1", target_method="m2"))
        code_graph.add_call(MethodCall(source_class="B", target_class="A", source_method="m2", target_method="m1"))

        violations = ViolationDetector.detect(arch_graph, code_graph)

        circular = [v for v in violations if v.type == "CIRCULAR_DEPENDENCY"]
        assert len(circular) > 0
        assert all(v.severity == "critical" for v in circular)

    def test_detect_multiple_violations_complex(self):
        """Test detecting multiple violations in complex graph."""
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("Controller", "layer1"))
        arch_graph.add_class(ArchitectureClass("Service", "layer2"))
        arch_graph.add_class(ArchitectureClass("Repository", "layer3"))
        arch_graph.add_edge(ArchitectureEdge("Controller", "Service", "calls"))
        arch_graph.add_edge(ArchitectureEdge("Service", "Repository", "calls"))

        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("Controller", "file.py", 1))
        code_graph.add_class(ClassDefinition("Service", "file.py", 10))
        code_graph.add_class(ClassDefinition("Repository", "file.py", 20))

        # Allowed calls
        code_graph.add_call(MethodCall("Controller", "Service", "handle", "process"))
        code_graph.add_call(MethodCall("Service", "Repository", "process", "query"))

        # Violation: Controller directly calls Repository
        code_graph.add_call(MethodCall("Controller", "Repository", "handle", "query"))

        violations = ViolationDetector.detect(arch_graph, code_graph)

        # Should detect the direct violation
        assert len(violations) > 0
        direct_violations = [v for v in violations if v.type == "DIRECT_VIOLATION"]
        assert len(direct_violations) > 0
