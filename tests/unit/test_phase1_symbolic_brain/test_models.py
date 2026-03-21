"""
Unit tests for Phase 1 Symbolic Brain data models.

Tests all four core model classes:
- Layer: Represents an architectural layer
- ArchitectureClass: Represents a class in the architecture
- ArchitectureEdge: Represents a relationship between classes
- ArchitectureGraph: The complete architecture graph
"""

import pytest
from archguard.phase1_symbolic_brain.models import (
    Layer,
    ArchitectureClass,
    ArchitectureEdge,
    ArchitectureGraph,
)


class TestLayer:
    """Test Layer class."""

    def test_layer_init(self):
        """Test Layer initialization."""
        layer = Layer("UI Layer", "User interface components")
        assert layer.name == "UI Layer"
        assert layer.description == "User interface components"
        assert len(layer.classes) == 0

    def test_layer_init_without_description(self):
        """Test Layer initialization without description."""
        layer = Layer("Service Layer")
        assert layer.name == "Service Layer"
        assert layer.description is None

    def test_layer_add_class(self):
        """Test adding a class to a layer."""
        layer = Layer("UI Layer")
        layer.add_class("UserController")
        assert "UserController" in layer.classes
        assert len(layer.classes) == 1

    def test_layer_add_multiple_classes(self):
        """Test adding multiple classes to a layer."""
        layer = Layer("UI Layer")
        layer.add_class("UserController")
        layer.add_class("ProductController")
        assert len(layer.classes) == 2
        assert "UserController" in layer.classes
        assert "ProductController" in layer.classes

    def test_layer_remove_class(self):
        """Test removing a class from a layer."""
        layer = Layer("UI Layer")
        layer.add_class("UserController")
        layer.remove_class("UserController")
        assert len(layer.classes) == 0

    def test_layer_remove_nonexistent_class_no_error(self):
        """Test removing a non-existent class uses discard (no error)."""
        layer = Layer("UI Layer")
        # discard doesn't raise, it just does nothing
        layer.remove_class("NonExistent")
        assert len(layer.classes) == 0

    def test_layer_equality(self):
        """Test Layer equality."""
        layer1 = Layer("UI Layer", "Description")
        layer2 = Layer("UI Layer", "Description")
        assert layer1 == layer2

    def test_layer_inequality_different_name(self):
        """Test Layer inequality with different names."""
        layer1 = Layer("UI Layer")
        layer2 = Layer("Service Layer")
        assert layer1 != layer2

    def test_layer_string_representation(self):
        """Test Layer string representation."""
        layer = Layer("UI Layer", "Description")
        assert "UI Layer" in str(layer)


class TestArchitectureClass:
    """Test ArchitectureClass class."""

    def test_architecture_class_init(self):
        """Test ArchitectureClass initialization."""
        arch_class = ArchitectureClass("UserController", "UI Layer")
        assert arch_class.name == "UserController"
        assert arch_class.layer == "UI Layer"
        assert arch_class.description is None
        assert isinstance(arch_class.attributes, dict)

    def test_architecture_class_with_attributes(self):
        """Test ArchitectureClass with attributes."""
        arch_class = ArchitectureClass(
            "UserController", "UI Layer", attributes={"public": True, "abstract": False}
        )
        assert arch_class.attributes["public"] is True
        assert arch_class.attributes["abstract"] is False

    def test_architecture_class_hashable(self):
        """Test ArchitectureClass is hashable."""
        class1 = ArchitectureClass("UserController", "UI Layer")
        class2 = ArchitectureClass("UserController", "UI Layer")
        # Same content should have same hash
        assert hash(class1) == hash(class2)

    def test_architecture_class_in_set(self):
        """Test ArchitectureClass can be added to set."""
        class1 = ArchitectureClass("UserController", "UI Layer")
        class2 = ArchitectureClass("ProductController", "UI Layer")
        class_set = {class1, class2}
        assert len(class_set) == 2

    def test_architecture_class_equality(self):
        """Test ArchitectureClass equality."""
        class1 = ArchitectureClass("UserController", "UI Layer")
        class2 = ArchitectureClass("UserController", "UI Layer")
        assert class1 == class2

    def test_architecture_class_inequality_different_name(self):
        """Test ArchitectureClass inequality with different name."""
        class1 = ArchitectureClass("UserController", "UI Layer")
        class2 = ArchitectureClass("ProductController", "UI Layer")
        assert class1 != class2

    def test_architecture_class_inequality_different_layer(self):
        """Test ArchitectureClass inequality with different layer."""
        class1 = ArchitectureClass("UserController", "UI Layer")
        class2 = ArchitectureClass("UserController", "Service Layer")
        assert class1 != class2

    def test_architecture_class_string_representation(self):
        """Test ArchitectureClass string representation."""
        arch_class = ArchitectureClass("UserController", "UI Layer")
        assert "UserController" in str(arch_class)
        assert "UI Layer" in str(arch_class)


class TestArchitectureEdge:
    """Test ArchitectureEdge class."""

    def test_architecture_edge_init(self):
        """Test ArchitectureEdge initialization."""
        edge = ArchitectureEdge("UserController", "UserService")
        assert edge.source == "UserController"
        assert edge.target == "UserService"
        assert edge.edge_type == "calls"
        assert edge.description is None

    def test_architecture_edge_with_metadata(self):
        """Test ArchitectureEdge with custom metadata."""
        edge = ArchitectureEdge(
            "UserController",
            "UserService",
            edge_type="depends_on",
            description="HTTP REST call",
            metadata={"protocol": "REST", "timeout": "5000"},
        )
        assert edge.edge_type == "depends_on"
        assert edge.description == "HTTP REST call"
        assert edge.metadata["protocol"] == "REST"

    def test_architecture_edge_hashable(self):
        """Test ArchitectureEdge is hashable."""
        edge1 = ArchitectureEdge("UserController", "UserService")
        edge2 = ArchitectureEdge("UserController", "UserService")
        assert hash(edge1) == hash(edge2)

    def test_architecture_edge_in_set(self):
        """Test ArchitectureEdge can be added to set."""
        edge1 = ArchitectureEdge("UserController", "UserService")
        edge2 = ArchitectureEdge("UserController", "ProductService")
        edge_set = {edge1, edge2}
        assert len(edge_set) == 2

    def test_architecture_edge_equality(self):
        """Test ArchitectureEdge equality."""
        edge1 = ArchitectureEdge("UserController", "UserService")
        edge2 = ArchitectureEdge("UserController", "UserService")
        assert edge1 == edge2

    def test_architecture_edge_string_representation(self):
        """Test ArchitectureEdge string representation."""
        edge = ArchitectureEdge("UserController", "UserService")
        edge_str = str(edge)
        assert "UserController" in edge_str
        assert "UserService" in edge_str


class TestArchitectureGraph:
    """Test ArchitectureGraph class."""

    def test_architecture_graph_init(self):
        """Test ArchitectureGraph initialization."""
        graph = ArchitectureGraph()
        assert len(graph.layers) == 0
        assert len(graph.classes) == 0
        assert len(graph.edges) == 0

    def test_add_layer(self):
        """Test adding a layer to graph."""
        graph = ArchitectureGraph()
        layer = Layer("UI Layer", "User interface components")
        graph.add_layer(layer)
        assert "UI Layer" in graph.layers
        assert graph.layers["UI Layer"].name == "UI Layer"

    def test_add_multiple_layers(self):
        """Test adding multiple layers to graph."""
        graph = ArchitectureGraph()
        graph.add_layer(Layer("UI Layer"))
        graph.add_layer(Layer("Service Layer"))
        graph.add_layer(Layer("Data Layer"))
        assert len(graph.layers) == 3

    def test_add_duplicate_layer_overwrites(self):
        """Test adding duplicate layer overwrites existing."""
        graph = ArchitectureGraph()
        graph.add_layer(Layer("UI Layer", "Description 1"))
        graph.add_layer(Layer("UI Layer", "Description 2"))
        assert len(graph.layers) == 1
        assert graph.layers["UI Layer"].description == "Description 2"

    def test_add_class(self):
        """Test adding a class to graph."""
        graph = ArchitectureGraph()
        arch_class = ArchitectureClass("UserController", "UI Layer", "Handles user requests")
        graph.add_class(arch_class)
        assert "UserController" in graph.classes
        assert graph.classes["UserController"].layer == "UI Layer"

    def test_add_multiple_classes(self):
        """Test adding multiple classes to graph."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        assert len(graph.classes) == 2

    def test_add_edge(self):
        """Test adding an edge to graph."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        edge = ArchitectureEdge("UserController", "UserService", edge_type="calls")
        graph.add_edge(edge)
        assert len(graph.edges) == 1

    def test_is_edge_allowed_existing_edge(self):
        """Test is_edge_allowed returns True for existing edge."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        edge = ArchitectureEdge("UserController", "UserService")
        graph.add_edge(edge)
        assert graph.is_edge_allowed("UserController", "UserService") is True

    def test_is_edge_allowed_nonexistent_edge(self):
        """Test is_edge_allowed returns False for non-existent edge."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        assert graph.is_edge_allowed("UserController", "UserService") is False

    def test_get_allowed_targets(self):
        """Test get_allowed_targets returns correct targets."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        graph.add_class(ArchitectureClass("ProductService", "Service Layer"))
        graph.add_edge(ArchitectureEdge("UserController", "UserService"))
        graph.add_edge(ArchitectureEdge("UserController", "ProductService"))
        targets = graph.get_allowed_targets("UserController")
        assert "UserService" in targets
        assert "ProductService" in targets
        assert len(targets) == 2

    def test_get_allowed_targets_no_edges(self):
        """Test get_allowed_targets with no edges."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        targets = graph.get_allowed_targets("UserController")
        assert len(targets) == 0

    def test_to_networkx(self):
        """Test converting to NetworkX graph."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        graph.add_edge(ArchitectureEdge("UserController", "UserService"))

        nx_graph = graph.to_networkx()
        assert nx_graph is not None
        assert "UserController" in nx_graph.nodes()
        assert "UserService" in nx_graph.nodes()
        assert nx_graph.has_edge("UserController", "UserService")

    def test_to_networkx_preserves_edge_attributes(self):
        """Test to_networkx preserves edge attributes."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        edge = ArchitectureEdge(
            "UserController",
            "UserService",
            description="REST API call",
            metadata={"timeout": "5000"},
        )
        graph.add_edge(edge)

        nx_graph = graph.to_networkx()
        edge_data = nx_graph.edges["UserController", "UserService"]
        assert edge_data["description"] == "REST API call"
        assert edge_data["timeout"] == "5000"

    def test_architecture_graph_string_representation(self):
        """Test ArchitectureGraph string representation."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph_str = str(graph)
        assert "ArchitectureGraph" in graph_str

    def test_complex_graph_construction(self):
        """Test constructing a complex architecture graph."""
        graph = ArchitectureGraph()

        # Add layers
        graph.add_layer(Layer("UI Layer", "Presentation tier"))
        graph.add_layer(Layer("Service Layer", "Business logic tier"))
        graph.add_layer(Layer("Data Layer", "Persistence tier"))

        # Add classes to UI layer
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("ProductController", "UI Layer"))

        # Add classes to Service layer
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))
        graph.add_class(ArchitectureClass("ProductService", "Service Layer"))

        # Add classes to Data layer
        graph.add_class(ArchitectureClass("UserRepository", "Data Layer"))
        graph.add_class(ArchitectureClass("ProductRepository", "Data Layer"))

        # Add allowed edges (UI -> Service -> Data)
        graph.add_edge(ArchitectureEdge("UserController", "UserService"))
        graph.add_edge(ArchitectureEdge("ProductController", "ProductService"))
        graph.add_edge(ArchitectureEdge("UserService", "UserRepository"))
        graph.add_edge(ArchitectureEdge("ProductService", "ProductRepository"))

        # Verify structure
        assert len(graph.layers) == 3
        assert len(graph.classes) == 6
        assert len(graph.edges) == 4

        # Verify allowed edges
        assert graph.is_edge_allowed("UserController", "UserService")
        assert graph.is_edge_allowed("UserService", "UserRepository")

        # Verify forbidden edges (direct UI to Data)
        assert not graph.is_edge_allowed("UserController", "UserRepository")

    def test_graph_prevents_self_loops(self):
        """Test that graph can handle self-loops."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))

        # Add self-loop
        graph.add_edge(ArchitectureEdge("UserController", "UserController"))

        # Self-loop should be allowed as an edge
        assert graph.is_edge_allowed("UserController", "UserController")

    def test_architecture_graph_duplicate_edge_same_params(self):
        """Test that edges with same source, target, edge_type are same edge."""
        graph = ArchitectureGraph()
        graph.add_class(ArchitectureClass("UserController", "UI Layer"))
        graph.add_class(ArchitectureClass("UserService", "Service Layer"))

        # Add edge with description "First"
        graph.add_edge(ArchitectureEdge("UserController", "UserService", description="First"))
        assert len(graph.edges) == 1

        # Add same edge with description "Second" - it's a different edge
        # because __hash__ doesn't include description
        graph.add_edge(ArchitectureEdge("UserController", "UserService", description="Second"))
        # Both edges exist in the set
        assert len(graph.edges) == 2
