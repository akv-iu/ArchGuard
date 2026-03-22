"""Tree-Sitter wrapper for Phase 2: Code Abstraction.

Uses Python's ast module for Python code parsing (Phase 2 is Python-focused).
This can be extended to use tree-sitter-languages for multi-language support in Phase 2b.
"""

import ast
from typing import Optional, Union
from pathlib import Path

from archguard.common.logger import get_logger

logger = get_logger(__name__)


class ParsedTree:
    """Wrapper around a parsed AST tree.

    Provides a consistent interface regardless of parsing backend.
    """

    def __init__(self, tree: ast.Module, source_code: str):
        """Initialize ParsedTree.

        Args:
            tree: Python AST Module node
            source_code: Original source code as string
        """
        self.tree = tree
        self.source_code = source_code

    def get_root_node(self) -> ast.Module:
        """Get the root AST node.

        Returns:
            Root AST Module node
        """
        return self.tree

    def find_classes(self) -> list:
        """Find all class definitions in the tree.

        Returns:
            List of ClassDef AST nodes
        """
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef)]

    def find_functions(self) -> list:
        """Find all function definitions in the tree.

        Returns:
            List of FunctionDef and AsyncFunctionDef AST nodes
        """
        return [node for node in ast.walk(self.tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def find_calls(self) -> list:
        """Find all function/method calls in the tree.

        Returns:
            List of Call AST nodes
        """
        return [node for node in ast.walk(self.tree) if isinstance(node, ast.Call)]


class TreeSitterWrapper:
    """Wrapper for parsing Python source code.

    Currently uses Python's ast module for Phase 2 (Python-focused implementation).
    Can be extended to support multiple languages via tree-sitter in future versions.
    """

    def __init__(self, language: str = "python"):
        """Initialize wrapper.

        Args:
            language: Programming language to parse (default: python)

        Raises:
            ValueError: If language is not supported
        """
        if language != "python":
            raise ValueError(f"Language '{language}' not yet supported. Currently only Python is supported.")

        self.language = language
        logger.info(f"Initialized Python AST parser for {language}")

    def parse_file(self, filepath: str) -> ParsedTree:
        """Parse a Python file.

        Args:
            filepath: Path to Python source file

        Returns:
            ParsedTree object with AST and source code

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file contains invalid Python syntax
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()

        logger.debug(f"Parsing Python file: {filepath}")
        return self.parse_string(source_code)

    def parse_string(self, code: str) -> ParsedTree:
        """Parse Python code from a string.

        Args:
            code: Python source code as string

        Returns:
            ParsedTree object with AST and source code

        Raises:
            SyntaxError: If code contains invalid Python syntax
        """
        try:
            tree = ast.parse(code)
            logger.debug("Successfully parsed Python code")
            return ParsedTree(tree, code)
        except SyntaxError as e:
            logger.error(f"Syntax error while parsing: {e}")
            raise
