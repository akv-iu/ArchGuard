"""Unit tests for TreeSitterWrapper.

Tests Python code parsing using ast module.
"""

import pytest
import tempfile
from pathlib import Path

from archguard.phase2_code_abstraction.tree_sitter_wrapper import TreeSitterWrapper, ParsedTree


class TestTreeSitterWrapper:
    """Tests for TreeSitterWrapper initialization and parsing."""

    def test_init_default_python(self):
        """Test initializing wrapper with default Python language."""
        wrapper = TreeSitterWrapper()
        assert wrapper.language == "python"

    def test_init_python_explicit(self):
        """Test initializing wrapper with explicit Python language."""
        wrapper = TreeSitterWrapper(language="python")
        assert wrapper.language == "python"

    def test_init_unsupported_language(self):
        """Test that unsupported languages raise ValueError."""
        with pytest.raises(ValueError, match="Language 'java' not yet supported"):
            TreeSitterWrapper(language="java")

    def test_parse_string_simple_class(self):
        """Test parsing a simple Python class from string."""
        code = "class MyClass:\n    pass"
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        assert isinstance(parsed, ParsedTree)
        assert parsed.source_code == code

    def test_parse_string_syntax_error(self):
        """Test that syntax errors raise SyntaxError."""
        code = "class MyClass\n    pass"  # Missing colon
        wrapper = TreeSitterWrapper()

        with pytest.raises(SyntaxError):
            wrapper.parse_string(code)

    def test_parse_file_exists(self, tmp_path):
        """Test parsing an existing Python file."""
        file = tmp_path / "test.py"
        file.write_text("class TestClass:\n    def method(self):\n        pass")

        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_file(str(file))

        assert isinstance(parsed, ParsedTree)
        assert "TestClass" in parsed.source_code

    def test_parse_file_not_exists(self):
        """Test that non-existent file raises FileNotFoundError."""
        wrapper = TreeSitterWrapper()

        with pytest.raises(FileNotFoundError):
            wrapper.parse_file("/nonexistent/path/file.py")

    def test_parse_file_syntax_error(self, tmp_path):
        """Test that file with syntax errors raises SyntaxError."""
        file = tmp_path / "bad.py"
        file.write_text("def function(\n")  # Incomplete function

        wrapper = TreeSitterWrapper()
        with pytest.raises(SyntaxError):
            wrapper.parse_file(str(file))

    def test_parse_empty_string(self):
        """Test parsing empty Python code."""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string("")

        assert isinstance(parsed, ParsedTree)
        assert parsed.source_code == ""

    def test_parse_multiline_code(self):
        """Test parsing multi-line Python code."""
        code = """
class FirstClass:
    def method1(self):
        pass

class SecondClass:
    def method2(self):
        pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        assert isinstance(parsed, ParsedTree)
        assert len(parsed.find_classes()) == 2


class TestParsedTree:
    """Tests for ParsedTree helper methods."""

    def test_get_root_node(self):
        """Test getting root node from parsed tree."""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string("class MyClass:\n    pass")

        root = parsed.get_root_node()
        assert root is not None

    def test_find_classes_empty(self):
        """Test finding classes in code with no classes."""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string("x = 5\ny = 10")

        classes = parsed.find_classes()
        assert len(classes) == 0

    def test_find_classes_multiple(self):
        """Test finding multiple classes."""
        code = """
class A:
    pass

class B:
    pass

class C:
    pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        classes = parsed.find_classes()
        assert len(classes) == 3
        class_names = [c.name for c in classes]
        assert set(class_names) == {"A", "B", "C"}

    def test_find_functions(self):
        """Test finding function definitions."""
        code = """
def function1():
    pass

def function2():
    pass

class MyClass:
    def method(self):
        pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        functions = parsed.find_functions()
        # Should find 3: function1, function2, and MyClass.method
        assert len(functions) >= 2

    def test_find_calls(self):
        """Test finding function/method calls."""
        code = """
class MyClass:
    def __init__(self, service):
        self.service = service

    def do_something(self):
        return self.service.get_data()
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        calls = parsed.find_calls()
        assert len(calls) > 0

    def test_find_nested_function_definitions(self):
        """Test finding nested function definitions."""
        code = """
class Outer:
    def outer_method(self):
        def inner_function():
            pass
        return inner_function
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        functions = parsed.find_functions()
        assert len(functions) >= 2  # outer_method and inner_function

    def test_parse_tree_preserves_source(self):
        """Test that ParsedTree preserves original source code."""
        original_code = "class X:\n    pass"
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(original_code)

        assert parsed.source_code == original_code
