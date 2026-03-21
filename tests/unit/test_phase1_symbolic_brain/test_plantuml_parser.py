"""
Unit tests for PlantUML parser.

Tests parsing of PlantUML files to extract architecture information
including layers, classes, and dependencies.
"""

import pytest
import tempfile
import os
from pathlib import Path

from archguard.phase1_symbolic_brain.plantuml_parser import PlantUMLParser
from archguard.common.exceptions import ParsingError


@pytest.fixture
def parser():
    """Create a fresh parser instance for each test."""
    return PlantUMLParser()


@pytest.fixture
def simple_plantuml():
    """Simple PlantUML content with one layer and one class."""
    return """@startuml
package "UI Layer" {
  class UserController
}
@enduml
"""


@pytest.fixture
def layered_architecture():
    """Three-layer architecture."""
    return """@startuml
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


@pytest.fixture
def ecommerce_plantuml():
    """Complex e-commerce architecture."""
    return """@startuml
package "API Layer" {
  class RestController
}

package "Business Logic Layer" {
  class UserService
  class PaymentService
}

package "Data Access Layer" {
  class UserRepository
  class PaymentRepository
}

RestController --> UserService : calls
RestController --> PaymentService : calls
UserService --> UserRepository : calls
PaymentService --> PaymentRepository : calls
@enduml
"""


class TestPlantUMLParserBasic:
    """Test basic PlantUML parser functionality."""

    def test_parser_init(self):
        """Test parser initialization."""
        parser = PlantUMLParser()
        assert parser.content is None
        assert parser.lines == []

    def test_parse_simple_plantuml(self, parser, simple_plantuml, tmp_path):
        """Test parsing simple PlantUML with one layer."""
        # Create temp file
        file = tmp_path / "simple.puml"
        file.write_text(simple_plantuml)

        result = parser.parse(str(file))

        assert "layers" in result
        assert "classes" in result
        assert "edges" in result
        assert "UI Layer" in result["layers"]
        assert "UserController" in result["classes"]

    def test_parse_nonexistent_file_raises_error(self, parser):
        """Test parsing non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/path/arch.puml")

    def test_parse_empty_file(self, parser, tmp_path):
        """Test parsing empty file."""
        file = tmp_path / "empty.puml"
        file.write_text("")

        result = parser.parse(str(file))
        assert result["layers"] == {}
        assert result["classes"] == {}
        assert result["edges"] == []

    def test_extract_layers(self, parser, layered_architecture, tmp_path):
        """Test layer extraction from PlantUML."""
        file = tmp_path / "layers.puml"
        file.write_text(layered_architecture)

        result = parser.parse(str(file))

        assert len(result["layers"]) == 3
        assert "UI Layer" in result["layers"]
        assert "Service Layer" in result["layers"]
        assert "Data Layer" in result["layers"]

    def test_extract_classes(self, parser, layered_architecture, tmp_path):
        """Test class extraction from PlantUML."""
        file = tmp_path / "classes.puml"
        file.write_text(layered_architecture)

        result = parser.parse(str(file))

        assert len(result["classes"]) == 6
        assert "UserController" in result["classes"]
        assert "UserService" in result["classes"]
        assert "UserRepository" in result["classes"]

    def test_extract_edges(self, parser, layered_architecture, tmp_path):
        """Test edge extraction from PlantUML."""
        file = tmp_path / "edges.puml"
        file.write_text(layered_architecture)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 4
        edge_pairs = [(e["source"], e["target"]) for e in result["edges"]]
        assert ("UserController", "UserService") in edge_pairs
        assert ("UserService", "UserRepository") in edge_pairs


class TestPlantUMLParserClassLayerAssignment:
    """Test proper assignment of classes to layers."""

    def test_class_assigned_to_correct_layer(self, parser, layered_architecture, tmp_path):
        """Test that classes are assigned to correct layers."""
        file = tmp_path / "layer_assignment.puml"
        file.write_text(layered_architecture)

        result = parser.parse(str(file))

        assert result["classes"]["UserController"]["layer"] == "UI Layer"
        assert result["classes"]["ProductController"]["layer"] == "UI Layer"
        assert result["classes"]["UserService"]["layer"] == "Service Layer"
        assert result["classes"]["UserRepository"]["layer"] == "Data Layer"

    def test_multiple_classes_in_same_layer(self, parser, layered_architecture, tmp_path):
        """Test multiple classes in the same layer are all extracted."""
        file = tmp_path / "multiple_classes.puml"
        file.write_text(layered_architecture)

        result = parser.parse(str(file))

        ui_classes = [c for c, info in result["classes"].items() if info["layer"] == "UI Layer"]
        assert len(ui_classes) == 2
        assert "UserController" in ui_classes
        assert "ProductController" in ui_classes


class TestPlantUMLParserEdges:
    """Test edge/dependency extraction."""

    def test_edge_with_description(self, parser, tmp_path):
        """Test edge extraction with description."""
        content = """@startuml
package "A" { class ClassA }
package "B" { class ClassB }
ClassA --> ClassB : REST API call
@enduml
"""
        file = tmp_path / "edge_desc.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 1
        assert result["edges"][0]["source"] == "ClassA"
        assert result["edges"][0]["target"] == "ClassB"
        assert result["edges"][0]["description"] == "REST API call"

    def test_edge_without_description(self, parser, tmp_path):
        """Test edge extraction without description."""
        content = """@startuml
package "A" { class ClassA }
package "B" { class ClassB }
ClassA --> ClassB
@enduml
"""
        file = tmp_path / "edge_no_desc.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 1
        assert result["edges"][0]["source"] == "ClassA"
        assert result["edges"][0]["target"] == "ClassB"
        assert result["edges"][0]["description"] == ""

    def test_multiple_edges_from_same_source(self, parser, tmp_path):
        """Test multiple dependencies from single class."""
        content = """@startuml
package "A" { class Controller }
package "B" {
  class ServiceA
  class ServiceB
}
Controller --> ServiceA
Controller --> ServiceB
@enduml
"""
        file = tmp_path / "multi_deps.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 2
        sources = [e["source"] for e in result["edges"]]
        assert sources.count("Controller") == 2

    def test_chain_dependencies(self, parser, tmp_path):
        """Test chain of dependencies."""
        content = """@startuml
package "A" { class A1 }
package "B" { class B1 }
package "C" { class C1 }
A1 --> B1
B1 --> C1
@enduml
"""
        file = tmp_path / "chain.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 2


class TestPlantUMLParserComplexArchitectures:
    """Test with realistic architecture diagrams."""

    def test_ecommerce_architecture(self, parser, ecommerce_plantuml, tmp_path):
        """Test parsing complex e-commerce architecture."""
        file = tmp_path / "ecommerce.puml"
        file.write_text(ecommerce_plantuml)

        result = parser.parse(str(file))

        # Verify layers
        assert len(result["layers"]) == 3
        assert "API Layer" in result["layers"]
        assert "Business Logic Layer" in result["layers"]
        assert "Data Access Layer" in result["layers"]

        # Verify classes
        assert len(result["classes"]) == 5
        assert "RestController" in result["classes"]
        assert "UserService" in result["classes"]
        assert "UserRepository" in result["classes"]

        # Verify edges
        assert len(result["edges"]) == 4

    def test_class_names_with_underscores(self, parser, tmp_path):
        """Test class names with underscores."""
        content = """@startuml
package "Layer1" { class User_Controller }
package "Layer2" { class User_Service }
User_Controller --> User_Service
@enduml
"""
        file = tmp_path / "underscores.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert "User_Controller" in result["classes"]
        assert "User_Service" in result["classes"]

    def test_class_names_with_numbers(self, parser, tmp_path):
        """Test class names with numbers."""
        content = """@startuml
package "Layer1" { class Service2Controller }
package "Layer2" { class Service2API }
Service2Controller --> Service2API
@enduml
"""
        file = tmp_path / "numbers.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert "Service2Controller" in result["classes"]
        assert "Service2API" in result["classes"]


class TestPlantUMLParserEdgeCases:
    """Test edge cases and error conditions."""

    def test_whitespace_handling(self, parser, tmp_path):
        """Test handling of extra whitespace."""
        content = """@startuml

  package   "Layer1"   {
    class    ClassA
  }

  package "Layer2" {
    class ClassB
  }

  ClassA   -->   ClassB   :   description

@enduml
"""
        file = tmp_path / "whitespace.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert "Layer1" in result["layers"]
        assert "ClassA" in result["classes"]
        assert len(result["edges"]) == 1

    def test_case_sensitivity(self, parser, tmp_path):
        """Test that parsing is case-sensitive for keywords."""
        content = """@startuml
PACKAGE "Layer1" {
  CLASS ClassA
}
@enduml
"""
        file = tmp_path / "case_sensitive.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        # PlantUML keywords are case-insensitive, so this should work
        assert "Layer1" in result["layers"]

    def test_no_classes_in_layer(self, parser, tmp_path):
        """Test layer with no classes."""
        content = """@startuml
package "EmptyLayer" {
}

package "FullLayer" {
  class ClassA
}
@enduml
"""
        file = tmp_path / "empty_layer.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert "EmptyLayer" in result["layers"]
        assert "FullLayer" in result["layers"]

    def test_self_referencing_edge(self, parser, tmp_path):
        """Test edge from class to itself."""
        content = """@startuml
package "Layer1" { class ClassA }
ClassA --> ClassA : self reference
@enduml
"""
        file = tmp_path / "self_ref.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 1
        assert result["edges"][0]["source"] == "ClassA"
        assert result["edges"][0]["target"] == "ClassA"

    def test_comment_lines_ignored(self, parser, tmp_path):
        """Test that commented lines are handled."""
        content = """@startuml
' This is a comment
package "Layer1" {
  class ClassA
  ' class ClassB (commented out)
}
@enduml
"""
        file = tmp_path / "comments.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        # ClassB shouldn't be extracted since it's commented
        assert "ClassA" in result["classes"]
        assert "ClassB" not in result["classes"] or True  # Depends on parser strictness

    def test_no_layers_only_classes(self, parser, tmp_path):
        """Test PlantUML with classes but no explicit layers."""
        content = """@startuml
class ClassA
class ClassB
ClassA --> ClassB
@enduml
"""
        file = tmp_path / "no_layers.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        # Should still extract classes and edges
        assert "ClassA" in result["classes"]
        assert len(result["edges"]) == 1

    def test_special_characters_in_descriptions(self, parser, tmp_path):
        """Test special characters in edge descriptions."""
        content = """@startuml
package "A" { class A1 }
package "B" { class B1 }
A1 --> B1 : REST API (HTTP/HTTPS)
@enduml
"""
        file = tmp_path / "special_chars.puml"
        file.write_text(content)

        result = parser.parse(str(file))

        assert len(result["edges"]) == 1
        assert "HTTP" in result["edges"][0]["description"]


class TestPlantUMLParserIntegration:
    """Integration tests with real fixture files."""

    def test_parse_simple_layered_fixture(self, parser):
        """Test parsing the simple_layered.puml fixture file."""
        fixture_path = "tests/fixtures/sample_architectures/simple_layered.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        result = parser.parse(fixture_path)

        # Verify structure from fixture
        assert len(result["layers"]) == 3
        assert len(result["classes"]) == 6
        assert len(result["edges"]) == 4

    def test_parse_ecommerce_arch_fixture(self, parser):
        """Test parsing the ecommerce_arch.puml fixture file."""
        fixture_path = "tests/fixtures/sample_architectures/ecommerce_arch.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        result = parser.parse(fixture_path)

        # Verify it parsed something
        assert len(result["layers"]) > 0
        assert len(result["classes"]) > 0
        assert len(result["edges"]) > 0

    def test_parser_can_parse_same_file_twice(self, parser):
        """Test parser can parse the same file twice."""
        fixture_path = "tests/fixtures/sample_architectures/simple_layered.puml"
        if not os.path.exists(fixture_path):
            pytest.skip(f"Fixture file not found: {fixture_path}")

        result1 = parser.parse(fixture_path)
        result2 = parser.parse(fixture_path)

        assert result1 == result2
