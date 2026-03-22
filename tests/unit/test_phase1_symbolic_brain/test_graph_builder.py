"""
Unit tests for Graph Builder.

Tests building ArchitectureGraph from parsed PlantUML data.
"""

import pytest

from archguard.phase1_symbolic_brain.graph_builder import GraphBuilder
from archguard.phase1_symbolic_brain.plantuml_parser import PlantUMLParser


@pytest.fixture
def simple_parsed_data():
    """Sample parsed data from PlantUML."""
    return {
        "layers": {
            "UI Layer": {"description": "User Interface", "classes": []},
            "Service Layer": {"description": "Business Logic", "classes": []},
            "Data Layer": {"description": "Persistence", "classes": []},
        },
        "classes": {
            "UserController": {"layer": "UI Layer", "description": "User Controller"},
            "UserService": {"layer": "Service Layer", "description": "User Service"},
            "UserRepository": {"layer": "Data Layer", "description": "User Repository"},
        },
        "edges": [
            {"source": "UserController", "target": "UserService", "description": "calls"},
            {"source": "UserService", "target": "UserRepository", "description": "calls"},
        ],
    }


@pytest.fixture
def complex_parsed_data():
    """Complex parsed data with multiple layers and classes."""
    return {
        "layers": {
            "API Layer": {"description": "REST API", "classes": []},
            "Business Logic Layer": {"description": "Services", "classes": []},
            "Data Access Layer": {"description": "Repositories", "classes": []},
        },
        "classes": {
            "RestController": {"layer": "API Layer", "description": "REST Controller"},
            "UserService": {"layer": "Business Logic Layer", "description": "User Service"},
            "PaymentService": {
                "layer": "Business Logic Layer",
                "description": "Payment Service",
            },
            "UserRepository": {
                "layer": "Data Access Layer",
                "description": "User Repository",
            },
            "PaymentRepository": {
                "layer": "Data Access Layer",
                "description": "Payment Repository",
            },
        },
        "edges": [
            {"source": "RestController", "target": "UserService", "description": "REST call"},
            {"source": "RestController", "target": "PaymentService", "description": "REST call"},
            {"source": "UserService", "target": "UserRepository", "description": "DB call"},
            {"source": "PaymentService", "target": "PaymentRepository", "description": "DB call"},
        ],
    }


@pytest.fixture
def empty_parsed_data():
    """Empty parsed data."""
    return {"layers": {}, "classes": {}, "edges": []}


class TestGraphBuilderBasic:
    """Test basic GraphBuilder functionality."""

    def test_build_from_simple_data(self, simple_parsed_data):
        """Test building graph from simple parsed data."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert graph is not None
        assert len(graph.layers) == 3
        assert len(graph.classes) == 3
        assert len(graph.edges) == 2

    def test_build_from_empty_data(self, empty_parsed_data):
        """Test building graph from empty data."""
        graph = GraphBuilder.build_from_parsed(empty_parsed_data)

        assert len(graph.layers) == 0
        assert len(graph.classes) == 0
        assert len(graph.edges) == 0

    def test_build_missing_keys(self):
        """Test building graph with missing keys in parsed data."""
        # Missing 'edges' key
        data = {"layers": {}, "classes": {}}
        graph = GraphBuilder.build_from_parsed(data)

        assert graph is not None
        assert len(graph.layers) == 0
        assert len(graph.classes) == 0
        assert len(graph.edges) == 0


class TestGraphBuilderLayers:
    """Test layer handling in graph builder."""

    def test_layers_added_correctly(self, simple_parsed_data):
        """Test layers are added correctly to graph."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert "UI Layer" in graph.layers
        assert "Service Layer" in graph.layers
        assert "Data Layer" in graph.layers

    def test_layer_descriptions_preserved(self, simple_parsed_data):
        """Test layer descriptions are preserved."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert graph.layers["UI Layer"].description == "User Interface"
        assert graph.layers["Service Layer"].description == "Business Logic"
        assert graph.layers["Data Layer"].description == "Persistence"

    def test_multiple_layers(self, complex_parsed_data):
        """Test multiple layers are handled correctly."""
        graph = GraphBuilder.build_from_parsed(complex_parsed_data)

        assert len(graph.layers) == 3
        assert all(layer_name in graph.layers for layer_name in complex_parsed_data["layers"])


class TestGraphBuilderClasses:
    """Test class handling in graph builder."""

    def test_classes_added_correctly(self, simple_parsed_data):
        """Test classes are added correctly to graph."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert "UserController" in graph.classes
        assert "UserService" in graph.classes
        assert "UserRepository" in graph.classes

    def test_class_layer_assignment(self, simple_parsed_data):
        """Test classes are assigned to correct layers."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert graph.classes["UserController"].layer == "UI Layer"
        assert graph.classes["UserService"].layer == "Service Layer"
        assert graph.classes["UserRepository"].layer == "Data Layer"

    def test_class_descriptions_preserved(self, simple_parsed_data):
        """Test class descriptions are preserved."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert graph.classes["UserController"].description == "User Controller"
        assert graph.classes["UserService"].description == "User Service"

    def test_multiple_classes_same_layer(self, complex_parsed_data):
        """Test multiple classes in same layer."""
        graph = GraphBuilder.build_from_parsed(complex_parsed_data)

        business_logic_classes = [
            c for c in graph.classes.values() if c.layer == "Business Logic Layer"
        ]
        assert len(business_logic_classes) == 2

    def test_class_without_description(self):
        """Test class without explicit description."""
        data = {
            "layers": {"Layer1": {"description": "Layer", "classes": []}},
            "classes": {"Class1": {"layer": "Layer1"}},  # No description key
            "edges": [],
        }
        graph = GraphBuilder.build_from_parsed(data)

        assert "Class1" in graph.classes
        assert graph.classes["Class1"].description == "Class1"  # Uses class name as default


class TestGraphBuilderEdges:
    """Test edge/dependency handling in graph builder."""

    def test_edges_added_correctly(self, simple_parsed_data):
        """Test edges are added correctly to graph."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        assert len(graph.edges) == 2
        assert graph.is_edge_allowed("UserController", "UserService")
        assert graph.is_edge_allowed("UserService", "UserRepository")

    def test_edge_descriptions_preserved(self, simple_parsed_data):
        """Test edge descriptions are preserved."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        edges_with_desc = list(graph.edges)
        descriptions = [e.description for e in edges_with_desc]
        assert all(d == "calls" for d in descriptions)

    def test_multiple_edges_from_same_source(self, complex_parsed_data):
        """Test multiple edges from same source."""
        graph = GraphBuilder.build_from_parsed(complex_parsed_data)

        targets = graph.get_allowed_targets("RestController")
        assert "UserService" in targets
        assert "PaymentService" in targets
        assert len(targets) == 2

    def test_edge_without_description(self):
        """Test edge without description."""
        data = {
            "layers": {
                "L1": {"description": "Layer1", "classes": []},
                "L2": {"description": "Layer2", "classes": []},
            },
            "classes": {
                "Class1": {"layer": "L1"},
                "Class2": {"layer": "L2"},
            },
            "edges": [{"source": "Class1", "target": "Class2"}],  # No description
        }
        graph = GraphBuilder.build_from_parsed(data)

        edges = list(graph.edges)
        assert len(edges) == 1
        assert edges[0].description == ""

    def test_edge_chain(self, simple_parsed_data):
        """Test chain of edges (A->B->C)."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        # Verify chain
        assert graph.is_edge_allowed("UserController", "UserService")
        assert graph.is_edge_allowed("UserService", "UserRepository")
        # But not direct UI to Data
        assert not graph.is_edge_allowed("UserController", "UserRepository")


class TestGraphBuilderComplexScenarios:
    """Test complex scenarios."""

    def test_complex_architecture(self, complex_parsed_data):
        """Test building complex architecture."""
        graph = GraphBuilder.build_from_parsed(complex_parsed_data)

        assert len(graph.layers) == 3
        assert len(graph.classes) == 5
        assert len(graph.edges) == 4

    def test_networkx_export(self, simple_parsed_data):
        """Test exporting to NetworkX DiGraph."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)
        nx_graph = GraphBuilder.to_networkx(graph)

        assert "UserController" in nx_graph.nodes()
        assert "UserService" in nx_graph.nodes()
        assert "UserRepository" in nx_graph.nodes()
        assert nx_graph.has_edge("UserController", "UserService")
        assert nx_graph.has_edge("UserService", "UserRepository")

    def test_networkx_edge_attributes(self, simple_parsed_data):
        """Test NetworkX export preserves edge attributes."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)
        nx_graph = GraphBuilder.to_networkx(graph)

        edge_data = nx_graph.edges["UserController", "UserService"]
        assert "edge_type" in edge_data
        assert edge_data["edge_type"] == "calls"

    def test_all_classes_have_layers(self, complex_parsed_data):
        """Test all classes have layer assignments."""
        graph = GraphBuilder.build_from_parsed(complex_parsed_data)

        for class_name, arch_class in graph.classes.items():
            assert arch_class.layer is not None
            assert arch_class.layer in graph.layers

    def test_graph_allows_validation(self, simple_parsed_data):
        """Test graph supports architectural validation."""
        graph = GraphBuilder.build_from_parsed(simple_parsed_data)

        # Allowed edges
        assert graph.is_edge_allowed("UserController", "UserService") is True
        assert graph.is_edge_allowed("UserService", "UserRepository") is True

        # Forbidden edges (not explicitly added)
        assert graph.is_edge_allowed("UserController", "UserRepository") is False
        assert graph.is_edge_allowed("UserRepository", "UserController") is False


class TestGraphBuilderIntegration:
    """Integration tests with parser output."""

    def test_build_from_parser_output(self, tmp_path):
        """Test building graph from actual parser output."""
        # Create a simple PlantUML file
        plantuml_content = """@startuml
package "Layer1" {
  class ClassA
}
package "Layer2" {
  class ClassB
}
ClassA --> ClassB
@enduml
"""
        file = tmp_path / "test.puml"
        file.write_text(plantuml_content)

        # Parse it
        parser = PlantUMLParser()
        parsed = parser.parse(str(file))

        # Build graph
        graph = GraphBuilder.build_from_parsed(parsed)

        # Verify
        assert len(graph.layers) == 2
        assert len(graph.classes) == 2
        assert len(graph.edges) == 1
        assert graph.is_edge_allowed("ClassA", "ClassB")

    def test_parser_to_graph_pipeline(self, tmp_path):
        """Test complete parser -> builder pipeline."""
        # Create PlantUML file
        plantuml_content = """@startuml
package "UI" {
  class Controller
}
package "Service" {
  class Service
}
package "Data" {
  class Repository
}
Controller --> Service
Service --> Repository
@enduml
"""
        file = tmp_path / "arch.puml"
        file.write_text(plantuml_content)

        # Parse
        parser = PlantUMLParser()
        parsed = parser.parse(str(file))

        # Build
        graph = GraphBuilder.build_from_parsed(parsed)

        # Verify 3-layer structure
        assert len(graph.layers) == 3
        assert "UI" in graph.layers
        assert "Service" in graph.layers
        assert "Data" in graph.layers

        # Verify classes
        assert len(graph.classes) == 3
        assert graph.classes["Controller"].layer == "UI"
        assert graph.classes["Service"].layer == "Service"
        assert graph.classes["Repository"].layer == "Data"

        # Verify edges and layering rules
        assert graph.is_edge_allowed("Controller", "Service")
        assert graph.is_edge_allowed("Service", "Repository")
        assert not graph.is_edge_allowed("Controller", "Repository")
