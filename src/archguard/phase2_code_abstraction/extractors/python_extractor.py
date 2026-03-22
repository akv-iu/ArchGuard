"""Python code extractor for Phase 2: Code Abstraction.

High-level interface for extracting architectural facts from Python source code.
Uses TreeSitterWrapper and ASTWalker internally.
"""

from typing import Dict, List

from archguard.common.logger import get_logger
from archguard.phase2_code_abstraction.tree_sitter_wrapper import TreeSitterWrapper
from archguard.phase2_code_abstraction.ast_walker import ASTWalker

logger = get_logger(__name__)


class PythonExtractor:
    """Extracts architectural facts from Python source code.

    Provides high-level interface for extracting classes and method calls
    from Python files or code strings.
    """

    def __init__(self):
        """Initialize Python extractor."""
        self.wrapper = TreeSitterWrapper(language="python")
        self.walker = ASTWalker()
        logger.info("Initialized Python code extractor")

    def extract_from_file(self, filepath: str) -> Dict:
        """Extract classes and method calls from a Python file.

        Args:
            filepath: Path to Python source file

        Returns:
            Dictionary with 'classes' and 'calls' keys containing extracted facts

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file contains invalid Python syntax
        """
        logger.debug(f"Extracting from Python file: {filepath}")

        # Parse the file
        parsed_tree = self.wrapper.parse_file(filepath)

        # Extract facts from AST
        extracted = self.walker.walk(parsed_tree)

        logger.debug(
            f"Extraction complete: {len(extracted['classes'])} classes, "
            f"{len(extracted['calls'])} method calls"
        )

        return extracted

    def extract_from_string(self, code: str) -> Dict:
        """Extract classes and method calls from Python code string.

        Args:
            code: Python source code as string

        Returns:
            Dictionary with 'classes' and 'calls' keys containing extracted facts

        Raises:
            SyntaxError: If code contains invalid Python syntax
        """
        logger.debug("Extracting from Python code string")

        # Parse the code
        parsed_tree = self.wrapper.parse_string(code)

        # Extract facts from AST
        extracted = self.walker.walk(parsed_tree)

        logger.debug(
            f"Extraction complete: {len(extracted['classes'])} classes, "
            f"{len(extracted['calls'])} method calls"
        )

        return extracted

    def extract_from_files(self, filepaths: List[str]) -> Dict:
        """Extract from multiple Python files.

        Args:
            filepaths: List of file paths to Python source files

        Returns:
            Dictionary with aggregated 'classes' and 'calls' from all files

        Raises:
            FileNotFoundError: If any file doesn't exist
            SyntaxError: If any file contains invalid Python syntax
        """
        all_classes = {}
        all_calls = []

        for filepath in filepaths:
            logger.debug(f"Extracting from {filepath}")
            extracted = self.extract_from_file(filepath)

            # Merge classes (assuming unique class names across files)
            all_classes.update(extracted["classes"])

            # Append calls
            all_calls.extend(extracted["calls"])

        logger.info(
            f"Extraction complete from {len(filepaths)} files: "
            f"{len(all_classes)} total classes, {len(all_calls)} total method calls"
        )

        return {
            "classes": all_classes,
            "calls": all_calls
        }
