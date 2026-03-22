"""Unit tests for CodeGraphBuilder.

Tests graph construction from extracted code data.
"""

import pytest

from archguard.phase2_code_abstraction.code_graph_builder import CodeGraphBuilder
from archguard.phase2_code_abstraction.models import ImplementationGraph, ClassDefinition, MethodCall
from archguard.phase2_code_abstraction.extractors.python_extractor import PythonExtractor


class TestCodeGraphBuilder:
    """Tests for CodeGraphBuilder."""

    def test_build_from_extracted_empty(self):
        """Test building graph from empty extracted data."""
        extracted = {"classes": {}, "calls": []}

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        assert isinstance(graph, ImplementationGraph)
        assert len(graph.classes) == 0
        assert len(graph.calls) == 0

    def test_build_from_extracted_single_class(self):
        """Test building graph with single class."""
        extracted = {
            "classes": {
                "MyClass": {
                    "name": "MyClass",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {}
                }
            },
            "calls": []
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        assert len(graph.classes) == 1
        assert "MyClass" in graph.classes
        assert graph.classes["MyClass"].name == "MyClass"

    def test_build_from_extracted_with_methods(self):
        """Test building graph preserves methods."""
        extracted = {
            "classes": {
                "MyClass": {
                    "name": "MyClass",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {
                        "method1": {"name": "method1", "line_number": 2},
                        "method2": {"name": "method2", "line_number": 3}
                    }
                }
            },
            "calls": []
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        assert len(graph.classes["MyClass"].methods) == 2
        assert "method1" in graph.classes["MyClass"].methods
        assert "method2" in graph.classes["MyClass"].methods

    def test_build_from_extracted_with_inheritance(self):
        """Test building graph preserves inheritance."""
        extracted = {
            "classes": {
                "Base": {
                    "name": "Base",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {}
                },
                "Derived": {
                    "name": "Derived",
                    "line_number": 5,
                    "base_classes": ["Base"],
                    "methods": {}
                }
            },
            "calls": []
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        assert len(graph.classes) == 2
        assert graph.classes["Derived"].base_classes == ["Base"]

    def test_build_from_extracted_with_calls(self):
        """Test building graph with method calls."""
        extracted = {
            "classes": {
                "ClassA": {
                    "name": "ClassA",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {"method_a": {"name": "method_a", "line_number": 2}}
                },
                "ClassB": {
                    "name": "ClassB",
                    "line_number": 5,
                    "base_classes": [],
                    "methods": {"method_b": {"name": "method_b", "line_number": 6}}
                }
            },
            "calls": [
                {
                    "source_class": "ClassA",
                    "source_method": "method_a",
                    "target_class": "ClassB",
                    "target_method": "method_b",
                    "call_type": "instance",
                    "line_number": 3
                }
            ]
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        assert len(graph.calls) == 1
        call = list(graph.calls)[0]
        assert call.source_class == "ClassA"
        assert call.target_class == "ClassB"

    def test_build_from_extracted_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            CodeGraphBuilder.build_from_extracted("not a dict")

    def test_build_from_extracted_missing_classes_key(self):
        """Test that missing 'classes' key raises ValueError."""
        with pytest.raises(ValueError, match="'classes' and 'calls' keys"):
            CodeGraphBuilder.build_from_extracted({"calls": []})

    def test_build_from_extracted_missing_calls_key(self):
        """Test that missing 'calls' key raises ValueError."""
        with pytest.raises(ValueError, match="'classes' and 'calls' keys"):
            CodeGraphBuilder.build_from_extracted({"classes": {}})

    def test_build_from_extracted_filters_invalid_calls(self):
        """Test that calls without source/target are filtered."""
        extracted = {
            "classes": {
                "ClassA": {
                    "name": "ClassA",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {}
                }
            },
            "calls": [
                {
                    "source_class": "ClassA",
                    "source_method": "method",
                    "target_class": None,  # Invalid
                    "target_method": "method",
                    "call_type": "instance",
                    "line_number": 0
                },
                {
                    "source_class": None,  # Invalid
                    "source_method": "method",
                    "target_class": "ClassA",
                    "target_method": "method",
                    "call_type": "instance",
                    "line_number": 0
                }
            ]
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        # Invalid calls should be filtered out
        assert len(graph.calls) == 0

    def test_build_from_extractor_single_file(self, tmp_path):
        """Test building graph from a single file using extractor."""
        file = tmp_path / "service.py"
        code = """
class UserService:
    def get_user(self, user_id):
        pass
"""
        file.write_text(code)

        extractor = PythonExtractor()
        graph = CodeGraphBuilder.from_file(extractor, str(file))

        assert isinstance(graph, ImplementationGraph)
        assert "UserService" in graph.classes

    def test_build_from_extractor_multiple_files(self, tmp_path):
        """Test building graph from multiple files using extractor."""
        file1 = tmp_path / "file1.py"
        file1.write_text("class ServiceA:\n    pass")

        file2 = tmp_path / "file2.py"
        file2.write_text("class ServiceB:\n    pass")

        extractor = PythonExtractor()
        graph = CodeGraphBuilder.build_from_extractor(extractor, [str(file1), str(file2)])

        assert len(graph.classes) == 2
        assert "ServiceA" in graph.classes
        assert "ServiceB" in graph.classes

    def test_graph_query_methods_work(self):
        """Test that resulting graph supports query methods."""
        extracted = {
            "classes": {
                "ClassA": {
                    "name": "ClassA",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {}
                },
                "ClassB": {
                    "name": "ClassB",
                    "line_number": 5,
                    "base_classes": [],
                    "methods": {}
                }
            },
            "calls": [
                {
                    "source_class": "ClassA",
                    "source_method": "method",
                    "target_class": "ClassB",
                    "target_method": "method",
                    "call_type": "instance",
                    "line_number": 0
                }
            ]
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)

        # Test query methods
        called_by_a = graph.get_classes_called_by("ClassA")
        assert "ClassB" in called_by_a

        callers_of_b = graph.get_callers_of("ClassB")
        assert "ClassA" in callers_of_b

    def test_graph_export_to_networkx(self):
        """Test exporting graph to NetworkX format."""
        extracted = {
            "classes": {
                "ClassA": {
                    "name": "ClassA",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {}
                },
                "ClassB": {
                    "name": "ClassB",
                    "line_number": 5,
                    "base_classes": [],
                    "methods": {}
                }
            },
            "calls": [
                {
                    "source_class": "ClassA",
                    "source_method": "method",
                    "target_class": "ClassB",
                    "target_method": "method",
                    "call_type": "instance",
                    "line_number": 0
                }
            ]
        }

        graph = CodeGraphBuilder.build_from_extracted(extracted)
        nx_graph = graph.to_networkx()

        # Check NetworkX structure
        assert "ClassA" in nx_graph.nodes()
        assert "ClassB" in nx_graph.nodes()
        assert ("ClassA", "ClassB") in nx_graph.edges()

    def test_build_with_filepath_parameter(self):
        """Test that filepath parameter is preserved."""
        extracted = {
            "classes": {
                "MyClass": {
                    "name": "MyClass",
                    "line_number": 1,
                    "base_classes": [],
                    "methods": {}
                }
            },
            "calls": []
        }

        filepath = "/path/to/file.py"
        graph = CodeGraphBuilder.build_from_extracted(extracted, filepath=filepath)

        # All classes should have the filepath
        assert graph.classes["MyClass"].file_path == filepath
