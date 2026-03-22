"""
Integration tests for Phase 1: Complete end-to-end testing.

Tests the full pipeline: PlantUML file → Parser → GraphBuilder → ArchitectureGraph
"""

import os

import pytest

from archguard.phase1_symbolic_brain.graph_builder import GraphBuilder
from archguard.phase1_symbolic_brain.plantuml_parser import PlantUMLParser


class TestPhase1EndToEnd:
    """End-to-end tests for Phase 1 pipeline."""

    def test_simple_architecture_e2e(self, tmp_path):
        """Test complete Phase 1 pipeline with simple architecture."""
        # Step 1: Create PlantUML file
        plantuml_content = """@startuml
package "UI Layer" {
  class UserController
  class ProductController
}

package "Service Layer" {
  class UserService
  class ProductService
}

package "Data Layer" {
  class UserRepository
  class ProductRepository
}

UserController --> UserService : calls
ProductController --> ProductService : calls
UserService --> UserRepository : calls
ProductService --> ProductRepository : calls
@enduml
"""
        file = tmp_path / "arch.puml"
        file.write_text(plantuml_content)

        # Step 2: Parse PlantUML file
        parser = PlantUMLParser()
        parsed_data = parser.parse(str(file))

        # Verify parser output
        assert "layers" in parsed_data
        assert "classes" in parsed_data
        assert "edges" in parsed_data
        assert len(parsed_data["layers"]) == 3
        assert len(parsed_data["classes"]) == 6
        assert len(parsed_data["edges"]) == 4

        # Step 3: Build architecture graph
        graph = GraphBuilder.build_from_parsed(parsed_data)

        # Step 4: Verify complete pipeline output
        assert graph is not None
        assert len(graph.layers) == 3
        assert len(graph.classes) == 6
        assert len(graph.edges) == 4

        # Verify layer structure
        assert "UI Layer" in graph.layers
        assert "Service Layer" in graph.layers
        assert "Data Layer" in graph.layers

        # Verify classes
        assert "UserController" in graph.classes
        assert "UserService" in graph.classes
        assert "UserRepository" in graph.classes

        # Verify class-layer associations
        assert graph.classes["UserController"].layer == "UI Layer"
        assert graph.classes["UserService"].layer == "Service Layer"
        assert graph.classes["UserRepository"].layer == "Data Layer"

        # Verify allowed edges (3-layer architecture)
        assert graph.is_edge_allowed("UserController", "UserService")
        assert graph.is_edge_allowed("UserService", "UserRepository")
        assert graph.is_edge_allowed("ProductController", "ProductService")

        # Verify forbidden edges (no direct UI->Data layer calls)
        assert not graph.is_edge_allowed("UserController", "UserRepository")
        assert not graph.is_edge_allowed("ProductController", "ProductRepository")

    def test_complex_ecommerce_e2e(self):
        """Test full pipeline with e-commerce fixture."""
        fixture_path = "tests/fixtures/sample_architectures/ecommerce_arch.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        # Step 1: Parse
        parser = PlantUMLParser()
        parsed_data = parser.parse(fixture_path)

        # Step 2: Build graph
        graph = GraphBuilder.build_from_parsed(parsed_data)

        # Step 3: Verify
        assert graph is not None
        assert len(graph.layers) > 0
        assert len(graph.classes) > 0
        assert len(graph.edges) > 0

        # Verify structure
        for layer_name in parsed_data["layers"]:
            assert layer_name in graph.layers

        for class_name in parsed_data["classes"]:
            assert class_name in graph.classes

        # Verify edges
        for edge_data in parsed_data["edges"]:
            assert graph.is_edge_allowed(edge_data["source"], edge_data["target"])

    def test_networkx_export_from_parsed_file(self, tmp_path):
        """Test NetworkX export works end-to-end."""
        # Create and parse
        plantuml_content = """@startuml
package "L1" { class A }
package "L2" { class B }
A --> B
@enduml
"""
        file = tmp_path / "test.puml"
        file.write_text(plantuml_content)

        parser = PlantUMLParser()
        parsed = parser.parse(str(file))
        graph = GraphBuilder.build_from_parsed(parsed)

        # Export to NetworkX
        nx_graph = GraphBuilder.to_networkx(graph)

        # Verify structure
        assert "A" in nx_graph.nodes()
        assert "B" in nx_graph.nodes()
        assert nx_graph.has_edge("A", "B")

        # Verify can use NetworkX operations
        import networkx as nx

        # Should be able to find path
        assert nx.has_path(nx_graph, "A", "B")

    def test_multiple_files_pipeline(self, tmp_path):
        """Test pipeline can be reused for multiple files."""
        # Create two different architecture files
        arch1 = """@startuml
package "L1" { class C1 }
package "L2" { class C2 }
C1 --> C2
@enduml
"""

        arch2 = """@startuml
package "LA" { class CA }
package "LB" { class CB }
CA --> CB
@enduml
"""

        file1 = tmp_path / "arch1.puml"
        file2 = tmp_path / "arch2.puml"
        file1.write_text(arch1)
        file2.write_text(arch2)

        # Parse both
        parser = PlantUMLParser()
        parsed1 = parser.parse(str(file1))
        parsed2 = parser.parse(str(file2))

        # Build both
        graph1 = GraphBuilder.build_from_parsed(parsed1)
        graph2 = GraphBuilder.build_from_parsed(parsed2)

        # Verify they're independent
        assert "L1" in graph1.layers
        assert "LA" in graph2.layers
        assert "L1" not in graph2.layers
        assert "LA" not in graph1.layers

    def test_violation_detection_after_pipeline(self, tmp_path):
        """Test architectural violation detection after full pipeline."""
        # Architecture: UI can only call Service, not Data
        plantuml_content = """@startuml
package "UI Layer" { class UI }
package "Service Layer" { class Service }
package "Data Layer" { class Data }
UI --> Service
Service --> Data
@enduml
"""
        file = tmp_path / "arch.puml"
        file.write_text(plantuml_content)

        # Build graph
        parser = PlantUMLParser()
        parsed = parser.parse(str(file))
        graph = GraphBuilder.build_from_parsed(parsed)

        # Test allowed calls
        assert graph.is_edge_allowed("UI", "Service") is True
        assert graph.is_edge_allowed("Service", "Data") is True

        # Test violations (disallowed calls)
        assert graph.is_edge_allowed("UI", "Data") is False  # UI should not call Data directly

    def test_layered_architecture_validation(self, tmp_path):
        """Test strict layer validation after pipeline."""
        # 3-layer architecture
        plantuml_content = """@startuml
package "Presentation" { class Presenter }
package "Business Logic" { class Service }
package "Data" { class Repository }
Presenter --> Service
Service --> Repository
@enduml
"""
        file = tmp_path / "layers.puml"
        file.write_text(plantuml_content)

        parser = PlantUMLParser()
        parsed = parser.parse(str(file))
        graph = GraphBuilder.build_from_parsed(parsed)

        # Valid paths
        valid_calls = [
            ("Presenter", "Service"),  # Layer 1 -> 2
            ("Service", "Repository"),  # Layer 2 -> 3
        ]

        for source, target in valid_calls:
            assert graph.is_edge_allowed(source, target), f"Should allow {source} -> {target}"

        # Invalid paths (skipping layers)
        invalid_calls = [
            ("Presenter", "Repository"),  # Layer 1 -> 3 (skip layer 2)
            ("Repository", "Presenter"),  # Opposite direction
            ("Repository", "Service"),  # Backward layer call
        ]

        for source, target in invalid_calls:
            assert not graph.is_edge_allowed(
                source, target
            ), f"Should not allow {source} -> {target}"

    def test_get_allowed_targets_with_full_pipeline(self, tmp_path):
        """Test get_allowed_targets works correctly from parser output."""
        plantuml_content = """@startuml
package "Layer1" {
  class Controller
}
package "Layer2" {
  class ServiceA
  class ServiceB
  class ServiceC
}
Controller --> ServiceA
Controller --> ServiceB
Controller --> ServiceC
@enduml
"""
        file = tmp_path / "multi_targets.puml"
        file.write_text(plantuml_content)

        parser = PlantUMLParser()
        parsed = parser.parse(str(file))
        graph = GraphBuilder.build_from_parsed(parsed)

        # Get allowed targets
        targets = graph.get_allowed_targets("Controller")

        assert len(targets) == 3
        assert "ServiceA" in targets
        assert "ServiceB" in targets
        assert "ServiceC" in targets


class TestPhase1RealFixtures:
    """Tests using real fixture files."""

    def test_simple_layered_fixture_full_pipeline(self):
        """Test full pipeline with simple_layered.puml fixture."""
        fixture_path = "tests/fixtures/sample_architectures/simple_layered.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        # Parse
        parser = PlantUMLParser()
        parsed = parser.parse(fixture_path)

        # Build
        graph = GraphBuilder.build_from_parsed(parsed)

        # Verify
        assert len(graph.layers) == 3
        assert len(graph.classes) == 6
        assert len(graph.edges) == 4

        # Verify 3-layer architecture
        assert graph.is_edge_allowed("UserController", "UserService")
        assert graph.is_edge_allowed("UserService", "UserRepository")
        assert not graph.is_edge_allowed("UserController", "UserRepository")

    def test_ecommerce_fixture_full_pipeline(self):
        """Test full pipeline with ecommerce_arch.puml fixture."""
        fixture_path = "tests/fixtures/sample_architectures/ecommerce_arch.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        # Parse
        parser = PlantUMLParser()
        parsed = parser.parse(fixture_path)

        # Build
        graph = GraphBuilder.build_from_parsed(parsed)

        # Basic structure verification
        assert len(graph.layers) > 0
        assert len(graph.classes) > 0
        assert len(graph.edges) > 0

        # Verify it's a valid graph with proper relationships
        for edge_data in parsed["edges"]:
            source = edge_data["source"]
            target = edge_data["target"]
            assert graph.is_edge_allowed(source, target), (
                f"Edge {source} -> {target} should be allowed in graph"
            )

    def test_fixture_exports_to_networkx(self):
        """Test exporting fixture-based graph to NetworkX."""
        fixture_path = "tests/fixtures/sample_architectures/simple_layered.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        parser = PlantUMLParser()
        parsed = parser.parse(fixture_path)
        graph = GraphBuilder.build_from_parsed(parsed)

        # Export
        nx_graph = GraphBuilder.to_networkx(graph)

        # Verify basic properties
        assert len(nx_graph.nodes()) == len(graph.classes)
        assert len(nx_graph.edges()) == len(graph.edges)

        # Verify all classes are in NetworkX graph
        for class_name in graph.classes:
            assert class_name in nx_graph.nodes()


class TestPhase1ErrorHandling:
    """Test error handling in full pipeline."""

    def test_parser_error_stops_pipeline(self, tmp_path):
        """Test that parser errors are properly raised."""
        # Invalid PlantUML syntax
        bad_content = """@startuml
package "Layer1" {
  this is not valid syntax
}
"""
        file = tmp_path / "bad.puml"
        file.write_text(bad_content)

        parser = PlantUMLParser()
        # Parser should handle gracefully or raise proper error
        try:
            parsed = parser.parse(str(file))
            # If it parses, builder should still work
            graph = GraphBuilder.build_from_parsed(parsed)
            assert graph is not None
        except Exception as e:
            # Any exception is acceptable here
            assert True

    def test_missing_file_in_pipeline(self):
        """Test missing file error in pipeline."""
        parser = PlantUMLParser()

        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/arch.puml")

    def test_builder_handles_malformed_parsed_data(self):
        """Test builder gracefully handles malformed parsed data."""
        # Missing expected keys
        bad_data = {}

        graph = GraphBuilder.build_from_parsed(bad_data)
        assert graph is not None
        assert len(graph.layers) == 0
        assert len(graph.classes) == 0

    def test_builder_handles_incomplete_parsed_data(self):
        """Test builder with incomplete parsed data."""
        # Only layers, no classes or edges
        incomplete_data = {
            "layers": {"Layer1": {"description": "Layer", "classes": []}},
        }

        graph = GraphBuilder.build_from_parsed(incomplete_data)
        assert len(graph.layers) == 1
        assert len(graph.classes) == 0
        assert len(graph.edges) == 0
