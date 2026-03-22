"""End-to-end integration tests for Phase 2 code abstraction pipeline.

Tests the complete flow: File → TreeSitterWrapper → Extractor → GraphBuilder → Graph
"""

import pytest
from pathlib import Path

from archguard.phase2_code_abstraction.extractors.python_extractor import PythonExtractor
from archguard.phase2_code_abstraction.code_graph_builder import CodeGraphBuilder
from archguard.phase2_code_abstraction.models import ImplementationGraph


class TestPhase2EndToEnd:
    """End-to-end tests for Phase 2 extraction pipeline."""

    def test_simple_service_e2e(self):
        """Test complete Phase 2 pipeline with simple_service.py fixture.

        This fixture has 3 classes in a simple layered architecture:
        - UserController (UI layer)
        - UserService (Service layer)
        - UserRepository (Data layer)

        Expected:
        - Extract 3 classes
        - Extract calls: Controller -> Service -> Repository
        - Build queryable ImplementationGraph
        """
        fixture_path = Path("tests/fixtures/sample_code/simple_service.py")
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

        # Step 1: Extract from file
        extractor = PythonExtractor()
        extracted = extractor.extract_from_file(str(fixture_path))

        # Verify extraction
        assert len(extracted["classes"]) == 3, "Should extract 3 classes"
        assert "UserController" in extracted["classes"]
        assert "UserService" in extracted["classes"]
        assert "UserRepository" in extracted["classes"]

        # Step 2: Build graph
        graph = CodeGraphBuilder.build_from_extracted(extracted, str(fixture_path))
        assert isinstance(graph, ImplementationGraph)

        # Step 3: Verify classes
        assert len(graph.classes) == 3
        assert graph.classes["UserController"].name == "UserController"
        assert graph.classes["UserService"].name == "UserService"
        assert graph.classes["UserRepository"].name == "UserRepository"

        # Step 4: Verify calls
        assert len(graph.calls) > 0, "Should extract at least one method call"

        # Step 5: Verify dependencies
        called_by_controller = graph.get_classes_called_by("UserController")
        assert "UserService" in called_by_controller

        called_by_service = graph.get_classes_called_by("UserService")
        assert "UserRepository" in called_by_service

    def test_ecommerce_service_with_inheritance_e2e(self):
        """Test E2E pipeline with ecommerce_service.py fixture.

        This fixture has inheritance and composition patterns:
        - BaseService (abstract base)
        - ProductService(BaseService)
        - OrderService(BaseService)
        - Repositories
        - Logger dependency (composition)

        Expected:
        - Extract class hierarchy
        - Extract cross-service calls (OrderService -> ProductService)
        - Extract repository dependencies
        """
        fixture_path = Path("tests/fixtures/sample_code/ecommerce_service.py")
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

        # Extract
        extractor = PythonExtractor()
        extracted = extractor.extract_from_file(str(fixture_path))

        # Verify base classes
        assert "BaseService" in extracted["classes"]
        assert "ProductService" in extracted["classes"]
        assert "OrderService" in extracted["classes"]

        # Verify inheritance
        assert "BaseService" in extracted["classes"]["ProductService"]["base_classes"]
        assert "BaseService" in extracted["classes"]["OrderService"]["base_classes"]

        # Build graph
        graph = CodeGraphBuilder.build_from_extracted(extracted, str(fixture_path))

        # Verify graph structure
        assert len(graph.classes) >= 4
        assert graph.classes["ProductService"].base_classes == ["BaseService"]
        assert graph.classes["OrderService"].base_classes == ["BaseService"]

        # Verify cross-service calls
        called_by_order = graph.get_classes_called_by("OrderService")
        assert "ProductService" in called_by_order

    def test_complex_service_with_advanced_patterns_e2e(self):
        """Test E2E pipeline with complex_service.py fixture.

        This fixture includes advanced Python patterns:
        - ABC (Abstract Base Classes)
        - @staticmethod and @classmethod
        - @property decorator
        - Complex method calls
        - Multiple dependency types

        Expected:
        - Extract classes despite decorators
        - Extract method calls between services
        - Build queryable graph
        """
        fixture_path = Path("tests/fixtures/sample_code/complex_service.py")
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

        # Extract
        extractor = PythonExtractor()
        extracted = extractor.extract_from_file(str(fixture_path))

        # Verify extraction despite complex patterns
        assert len(extracted["classes"]) > 0, "Should extract classes"

        # Build graph
        graph = CodeGraphBuilder.build_from_extracted(extracted, str(fixture_path))
        assert isinstance(graph, ImplementationGraph)
        assert len(graph.classes) > 0

    def test_multiple_files_e2e(self, tmp_path):
        """Test E2E pipeline with multiple files.

        Extracts from multiple files and builds unified graph.
        """
        # Create test files
        file1 = tmp_path / "service_a.py"
        file1.write_text("""
class ServiceA:
    def operation(self):
        pass
""")

        file2 = tmp_path / "service_b.py"
        file2.write_text("""
class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a

    def process(self):
        return self.service_a.operation()
""")

        # Extract from multiple files
        extractor = PythonExtractor()
        extracted = extractor.extract_from_files([str(file1), str(file2)])

        # Verify aggregation
        assert len(extracted["classes"]) == 2
        assert "ServiceA" in extracted["classes"]
        assert "ServiceB" in extracted["classes"]
        assert len(extracted["calls"]) > 0

        # Build graph
        graph = CodeGraphBuilder.build_from_extracted(extracted)

        # Verify unified graph
        assert len(graph.classes) == 2
        assert "ServiceA" in graph.get_classes_called_by("ServiceB")

    def test_graph_export_to_networkx_e2e(self):
        """Test that graph can be exported to NetworkX for analysis.

        This is crucial for Phase 3 (Logic Engine) which compares graphs.
        """
        fixture_path = Path("tests/fixtures/sample_code/simple_service.py")
        assert fixture_path.exists()

        # Extract and build
        extractor = PythonExtractor()
        extracted = extractor.extract_from_file(str(fixture_path))
        graph = CodeGraphBuilder.build_from_extracted(extracted, str(fixture_path))

        # Export to NetworkX
        nx_graph = graph.to_networkx()

        # Verify NetworkX structure
        assert nx_graph is not None
        assert len(nx_graph.nodes()) == 3
        assert len(nx_graph.edges()) >= 2

        # Verify graph traversal works (needed for Phase 3)
        assert "UserController" in nx_graph.nodes()
        assert "UserService" in nx_graph.nodes()
        assert ("UserController", "UserService") in nx_graph.edges()

    def test_query_methods_e2e(self):
        """Test that query methods work end-to-end.

        These are essential for Phase 3 violation detection.
        """
        fixture_path = Path("tests/fixtures/sample_code/simple_service.py")
        assert fixture_path.exists()

        extractor = PythonExtractor()
        extracted = extractor.extract_from_file(str(fixture_path))
        graph = CodeGraphBuilder.build_from_extracted(extracted, str(fixture_path))

        # Test get_classes_called_by
        controller_calls = graph.get_classes_called_by("UserController")
        assert isinstance(controller_calls, set)
        assert "UserService" in controller_calls

        # Test get_callers_of
        service_callers = graph.get_callers_of("UserService")
        assert isinstance(service_callers, set)
        assert "UserController" in service_callers

        # Test has_call
        assert graph.has_call("UserController", "UserService")
        assert not graph.has_call("UserRepository", "UserController")  # Reverse should be false

        # Test get_all_dependencies
        all_deps = graph.get_all_dependencies()
        assert isinstance(all_deps, set)
        assert len(all_deps) > 0

    def test_graph_length_and_properties_e2e(self):
        """Test graph length and property access."""
        fixture_path = Path("tests/fixtures/sample_code/simple_service.py")
        assert fixture_path.exists()

        extractor = PythonExtractor()
        extracted = extractor.extract_from_file(str(fixture_path))
        graph = CodeGraphBuilder.build_from_extracted(extracted, str(fixture_path))

        # Test __len__
        assert len(graph) == len(graph.classes)
        assert len(graph) == 3

        # Test class access
        controller = graph.classes["UserController"]
        assert controller.name == "UserController"
        assert controller.file_path == str(fixture_path)
        assert isinstance(controller.line_number, int)

    def test_full_pipeline_from_fixture_files(self):
        """Orchestrated test of full Phase 2 pipeline using all fixtures.

        Simulates what Phase 3 will do: collect all code facts and compare to architecture.
        """
        fixtures_dir = Path("tests/fixtures/sample_code")
        assert fixtures_dir.exists(), f"Fixtures directory not found: {fixtures_dir}"

        fixture_files = list(fixtures_dir.glob("*.py"))
        assert len(fixture_files) == 3, f"Expected 3 fixture files, found {len(fixture_files)}"

        # Extract from all fixtures
        extractor = PythonExtractor()
        all_extracted = {"classes": {}, "calls": []}

        for fixture_file in fixture_files:
            extracted = extractor.extract_from_file(str(fixture_file))
            all_extracted["classes"].update(extracted["classes"])
            all_extracted["calls"].extend(extracted["calls"])

        # Build unified graph
        graph = CodeGraphBuilder.build_from_extracted(all_extracted)

        # Verify comprehensive graph
        assert len(graph.classes) >= 9  # At least 9 classes from all fixtures
        assert len(graph.calls) >= 3  # At least 3 calls

        # Can query across all fixtures
        called_by_controller = graph.get_classes_called_by("UserController")
        assert len(called_by_controller) > 0

        # Export for comparison with architecture (Phase 3)
        nx_graph = graph.to_networkx()
        assert nx_graph is not None
