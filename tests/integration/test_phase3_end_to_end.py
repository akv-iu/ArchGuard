"""End-to-end integration tests for Phase 3: Logic Engine."""

import pytest

from archguard.phase1_symbolic_brain.models import ArchitectureClass, ArchitectureEdge, ArchitectureGraph
from archguard.phase2_code_abstraction.extractors.python_extractor import PythonExtractor
from archguard.phase2_code_abstraction.code_graph_builder import CodeGraphBuilder
from archguard.phase2_code_abstraction.models import ClassDefinition, ImplementationGraph, MethodCall
from archguard.phase3_logic_engine.violation_detector import ViolationDetector
from archguard.phase3_logic_engine.trace_generator import TraceGenerator
from archguard.phase3_logic_engine.models import Violation, ViolationReport


class TestPhase3EndToEnd:
    """End-to-end tests for Phase 3: Logic Engine."""

    def test_simple_violation_detection_e2e(self):
        """Test complete pipeline: Architecture → Code → Violations."""
        # Step 1: Create architecture (Phase 1)
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("UserController", "layer1"))
        arch_graph.add_class(ArchitectureClass("UserService", "layer2"))
        arch_graph.add_edge(ArchitectureEdge("UserController", "UserService", "calls"))

        # Step 2: Create code (Phase 2)
        code = """
class UserService:
    def get_user(self, user_id):
        return {}

class UserController:
    def __init__(self, service):
        self.service = service

    def handle_request(self, user_id):
        return self.service.get_user(user_id)
"""

        extractor = PythonExtractor()
        extracted = extractor.extract_from_string(code)
        code_graph = CodeGraphBuilder.build_from_extracted(extracted)

        # Step 3: Detect violations (Phase 3)
        violations = ViolationDetector.detect(arch_graph, code_graph)

        # No violations expected - code follows architecture
        assert len(violations) == 0

    def test_violation_detection_direct_violation_e2e(self):
        """Test detecting direct architectural violations."""
        # Architecture: Controller → Service → Repository (3-layer)
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("UserController", "ui"))
        arch_graph.add_class(ArchitectureClass("UserService", "business"))
        arch_graph.add_class(ArchitectureClass("UserRepository", "data"))
        arch_graph.add_edge(ArchitectureEdge("UserController", "UserService", "calls"))
        arch_graph.add_edge(ArchitectureEdge("UserService", "UserRepository", "calls"))

        # Code: Controller directly calls Repository (violation!)
        code = """
class UserRepository:
    def find_by_id(self, user_id):
        return {"id": user_id}

class UserService:
    def __init__(self, repo):
        self.repo = repo

    def get_user(self, user_id):
        return self.repo.find_by_id(user_id)

class UserController:
    def __init__(self, service, repo):
        self.service = service
        self.repo = repo

    def handle_request(self, user_id):
        # VIOLATION: Direct call to repository
        return self.repo.find_by_id(user_id)
"""

        extractor = PythonExtractor()
        extracted = extractor.extract_from_string(code)
        code_graph = CodeGraphBuilder.build_from_extracted(extracted)

        violations = ViolationDetector.detect(arch_graph, code_graph)

        # Should detect violation
        assert len(violations) > 0

    def test_violation_generation_e2e(self):
        """Test complete violation detection and trace generation."""
        # Create simple architecture
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("View", "layer1"))
        arch_graph.add_class(ArchitectureClass("Service", "layer2"))
        arch_graph.add_class(ArchitectureClass("Database", "layer3"))
        arch_graph.add_edge(ArchitectureEdge("View", "Service", "calls"))
        arch_graph.add_edge(ArchitectureEdge("Service", "Database", "calls"))

        # Create code with violation
        code_graph = ImplementationGraph()
        code_graph.add_class(ClassDefinition("View", "view.py", 1))
        code_graph.add_class(ClassDefinition("Service", "service.py", 10))
        code_graph.add_class(ClassDefinition("Database", "database.py", 20))

        # Allowed: View → Service
        code_graph.add_call(MethodCall(source_class="View", source_method="Service", target_class="render", target_method="process"))
        # Allowed: Service → Database
        code_graph.add_call(MethodCall(source_class="Service", source_method="Database", target_class="process", target_method="query"))
        # Violation: View → Database
        code_graph.add_call(MethodCall(source_class="View", source_method="Database", target_class="render", target_method="query"))

        # Detect violations
        violations = ViolationDetector.detect(arch_graph, code_graph)
        assert len(violations) > 0

        # Generate traces
        json_output = TraceGenerator.generate_json_traces(violations)
        assert "violations" in json_output

        # Generate human-readable
        human_report = TraceGenerator.generate_human_readable(violations)
        assert len(human_report) > 0

    def test_complex_architecture_e2e(self):
        """Test with complex multi-layer architecture."""
        # 4-layer architecture
        arch_graph = ArchitectureGraph()
        arch_graph.add_class(ArchitectureClass("UI", "layer1"))
        arch_graph.add_class(ArchitectureClass("Controller", "layer2"))
        arch_graph.add_class(ArchitectureClass("Service", "layer3"))
        arch_graph.add_class(ArchitectureClass("Repository", "layer4"))

        arch_graph.add_edge(ArchitectureEdge("UI", "Controller", "calls"))
        arch_graph.add_edge(ArchitectureEdge("Controller", "Service", "calls"))
        arch_graph.add_edge(ArchitectureEdge("Service", "Repository", "calls"))

        # Create code
        code_graph = ImplementationGraph()
        for cls in ["UI", "Controller", "Service", "Repository"]:
            code_graph.add_class(ClassDefinition(cls, "app.py", 0))

        # Follow architecture
        code_graph.add_call(MethodCall(source_class="UI", source_method="Controller", target_class="m1", target_method="m2"))
        code_graph.add_call(MethodCall(source_class="Controller", source_method="Service", target_class="m2", target_method="m3"))
        code_graph.add_call(MethodCall(source_class="Service", source_method="Repository", target_class="m3", target_method="m4"))

        violations = ViolationDetector.detect(arch_graph, code_graph)

        # No violations when following architecture
        assert len(violations) == 0

    def test_violation_classification_e2e(self):
        """Test classifying violations by type and severity."""
        v1 = Violation("DIRECT_VIOLATION", "A", "B", severity="high")
        v2 = Violation("TRANSITIVE_VIOLATION", "C", "D", severity="medium")
        violations = {v1, v2}

        classification = ViolationDetector.classify_violations(violations)

        assert len(classification["direct"]) == 1
        assert len(classification["transitive"]) == 1

    def test_report_generation_e2e(self):
        """Test complete report generation from violations."""
        violations = {
            Violation("DIRECT_VIOLATION", "A", "B", severity="high"),
            Violation("DIRECT_VIOLATION", "C", "D", severity="high"),
            Violation("TRANSITIVE_VIOLATION", "E", "F", severity="medium"),
        }

        # Create report
        report = ViolationReport()
        for v in violations:
            report.add_violation(v)

        # Verify report statistics
        assert report.total_violations == 3
        assert report.direct_violations == 2
        assert report.transitive_violations == 1

        # Convert to JSON
        report_dict = report.to_dict()
        assert report_dict["total_violations"] == 3
