"""Unit tests for PythonExtractor.

Tests high-level extraction interface.
"""

import pytest
import tempfile
from pathlib import Path

from archguard.phase2_code_abstraction.extractors.python_extractor import PythonExtractor


class TestPythonExtractor:
    """Tests for PythonExtractor high-level interface."""

    def test_init(self):
        """Test PythonExtractor initialization."""
        extractor = PythonExtractor()
        assert extractor.wrapper is not None
        assert extractor.walker is not None

    def test_extract_from_string_simple(self):
        """Test extracting from simple code string."""
        code = """
class UserService:
    def get_user(self):
        pass
"""
        extractor = PythonExtractor()
        result = extractor.extract_from_string(code)

        assert "classes" in result
        assert "calls" in result
        assert "UserService" in result["classes"]

    def test_extract_from_string_with_calls(self):
        """Test extracting code with method calls."""
        code = """
class A:
    def method(self):
        pass

class B:
    def __init__(self, a):
        self.a = a

    def process(self):
        return self.a.method()
"""
        extractor = PythonExtractor()
        result = extractor.extract_from_string(code)

        assert len(result["calls"]) > 0
        # Should find call from B to A
        assert any(
            c["source_class"] == "B" and c["target_class"] == "A"
            for c in result["calls"]
        )

    def test_extract_from_file(self, tmp_path):
        """Test extracting from a file."""
        file = tmp_path / "service.py"
        code = """
class UserService:
    def get_user(self, user_id):
        pass

    def save_user(self, user_id, data):
        pass
"""
        file.write_text(code)

        extractor = PythonExtractor()
        result = extractor.extract_from_file(str(file))

        assert "UserService" in result["classes"]
        assert "get_user" in result["classes"]["UserService"]["methods"]
        assert "save_user" in result["classes"]["UserService"]["methods"]

    def test_extract_from_file_not_exists(self):
        """Test that non-existent file raises FileNotFoundError."""
        extractor = PythonExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract_from_file("/nonexistent/file.py")

    def test_extract_from_file_syntax_error(self, tmp_path):
        """Test that syntax error in file raises SyntaxError."""
        file = tmp_path / "bad.py"
        file.write_text("class MyClass(\n")  # Incomplete

        extractor = PythonExtractor()
        with pytest.raises(SyntaxError):
            extractor.extract_from_file(str(file))

    def test_extract_from_files_multiple(self, tmp_path):
        """Test extracting from multiple files."""
        file1 = tmp_path / "file1.py"
        file1.write_text("class Service1:\n    pass")

        file2 = tmp_path / "file2.py"
        file2.write_text("class Service2:\n    pass")

        extractor = PythonExtractor()
        result = extractor.extract_from_files([str(file1), str(file2)])

        assert "Service1" in result["classes"]
        assert "Service2" in result["classes"]
        assert len(result["classes"]) == 2

    def test_extract_from_files_aggregates_calls(self, tmp_path):
        """Test that extract_from_files aggregates calls from all files."""
        file1 = tmp_path / "file1.py"
        file1.write_text("""
class A:
    def method(self):
        pass
""")

        file2 = tmp_path / "file2.py"
        file2.write_text("""
class B:
    def __init__(self, a):
        self.a = a

    def process(self):
        return self.a.method()
""")

        extractor = PythonExtractor()
        result = extractor.extract_from_files([str(file1), str(file2)])

        # Should have calls from both files
        assert len(result["calls"]) > 0

    def test_extract_inheritance_patterns(self):
        """Test extracting inheritance patterns."""
        code = """
class BaseService:
    def __init__(self, repo):
        self.repo = repo

class UserService(BaseService):
    def get_user(self, user_id):
        return self.repo.find_by_id(user_id)
"""
        extractor = PythonExtractor()
        result = extractor.extract_from_string(code)

        assert "BaseService" in result["classes"]
        assert "UserService" in result["classes"]
        assert "BaseService" in result["classes"]["UserService"]["base_classes"]

    def test_extract_composition_patterns(self):
        """Test extracting composition patterns."""
        code = """
class Repository:
    def find_by_id(self, id):
        pass

class Service:
    def __init__(self, repo):
        self.repo = repo

    def get_item(self, id):
        return self.repo.find_by_id(id)
"""
        extractor = PythonExtractor()
        result = extractor.extract_from_string(code)

        calls = result["calls"]
        # Should find call from Service to Repository
        assert any(
            c["source_class"] == "Service" and
            c["target_class"] == "Repository"
            for c in calls
        )

    def test_extract_from_empty_file(self, tmp_path):
        """Test extracting from empty Python file."""
        file = tmp_path / "empty.py"
        file.write_text("")

        extractor = PythonExtractor()
        result = extractor.extract_from_file(str(file))

        assert result["classes"] == {}
        assert result["calls"] == []

    def test_extract_with_only_functions(self):
        """Test extracting file with only functions (no classes)."""
        code = """
def function1():
    pass

def function2():
    pass
"""
        extractor = PythonExtractor()
        result = extractor.extract_from_string(code)

        # Should extract functions but no classes
        assert len(result["classes"]) == 0
