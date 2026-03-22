"""Unit tests for ASTWalker.

Tests AST extraction of classes, methods, and calls.
"""

import pytest

from archguard.phase2_code_abstraction.tree_sitter_wrapper import TreeSitterWrapper
from archguard.phase2_code_abstraction.ast_walker import ASTWalker


class TestASTWalker:
    """Tests for ASTWalker extraction logic."""

    def test_init(self):
        """Test ASTWalker initialization."""
        walker = ASTWalker()
        assert walker.classes == {}
        assert walker.calls == []
        assert walker.current_class is None
        assert walker.current_method is None

    def test_walk_empty_code(self):
        """Test walking empty code."""
        code = ""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        assert result["classes"] == {}
        assert result["calls"] == []

    def test_walk_single_class(self):
        """Test walking code with single class."""
        code = "class MyClass:\n    pass"
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        assert "MyClass" in result["classes"]
        assert result["classes"]["MyClass"]["name"] == "MyClass"

    def test_walk_class_with_base(self):
        """Test walking class with base class."""
        code = """
class Base:
    pass

class Derived(Base):
    pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        assert "Derived" in result["classes"]
        assert "Base" in result["classes"]["Derived"]["base_classes"]

    def test_walk_class_with_multiple_bases(self):
        """Test class with multiple base classes."""
        code = """
class A:
    pass

class B:
    pass

class C(A, B):
    pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        assert len(result["classes"]["C"]["base_classes"]) == 2
        assert "A" in result["classes"]["C"]["base_classes"]
        assert "B" in result["classes"]["C"]["base_classes"]

    def test_walk_class_with_methods(self):
        """Test walking class with methods."""
        code = """
class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        assert "MyClass" in result["classes"]
        methods = result["classes"]["MyClass"]["methods"]
        assert "method1" in methods
        assert "method2" in methods

    def test_walk_method_calls_self(self):
        """Test walking method calls to self."""
        code = """
class MyClass:
    def __init__(self, service):
        self.service = service

    def method1(self):
        return self.service.get()
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        calls = result["calls"]
        # Should find call to service.get()
        assert len(calls) > 0
        # At least one call should be from MyClass.method1
        assert any(c["source_class"] == "MyClass" for c in calls)

    def test_walk_method_calls_between_classes(self):
        """Test walking method calls between different classes."""
        code = """
class ServiceA:
    def do_work(self):
        pass

class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a

    def process(self):
        return self.service_a.do_work()
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        calls = result["calls"]
        # Should find call from ServiceB.process to ServiceA.do_work
        assert len(calls) > 0
        assert any(
            c["source_class"] == "ServiceB" and
            c["target_class"] == "ServiceA"
            for c in calls
        )

    def test_walk_multiple_classes(self):
        """Test walking multiple classes."""
        code = """
class ClassA:
    pass

class ClassB:
    pass

class ClassC:
    pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        assert len(result["classes"]) == 3
        assert "ClassA" in result["classes"]
        assert "ClassB" in result["classes"]
        assert "ClassC" in result["classes"]

    def test_walk_with_line_numbers(self):
        """Test that line numbers are captured."""
        code = """
class MyClass:
    def method(self):
        pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        # Line numbers should be >= 1
        assert result["classes"]["MyClass"]["line_number"] > 0
        assert result["classes"]["MyClass"]["methods"]["method"]["line_number"] > 0

    def test_walk_chained_calls(self):
        """Test walking chained method calls."""
        code = """
class Model:
    def filter(self):
        return self

    def get(self):
        return self

class Service:
    def __init__(self, model):
        self.model = model

    def fetch(self):
        return self.model.filter().get()
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        calls = result["calls"]
        # Should find calls from Service to Model
        assert any(
            c["source_class"] == "Service" and
            c["target_class"] == "Model"
            for c in calls
        )

    def test_walk_async_methods(self):
        """Test walking async method definitions."""
        code = """
class AsyncService:
    async def fetch(self):
        pass

    async def process(self):
        pass
"""
        wrapper = TreeSitterWrapper()
        parsed = wrapper.parse_string(code)

        walker = ASTWalker()
        result = walker.walk(parsed)

        methods = result["classes"]["AsyncService"]["methods"]
        assert "fetch" in methods
        assert "process" in methods
