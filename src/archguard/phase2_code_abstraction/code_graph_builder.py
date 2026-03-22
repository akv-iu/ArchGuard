"""Code graph builder for Phase 2: Code Abstraction.

Converts extracted code facts into typed ImplementationGraph objects.
Follows same pattern as Phase 1's GraphBuilder for consistency.
"""

from typing import Dict, List

from archguard.common.logger import get_logger
from archguard.phase2_code_abstraction.models import (
    ClassDefinition,
    MethodDefinition,
    MethodCall,
    ImplementationGraph
)

logger = get_logger(__name__)


class CodeGraphBuilder:
    """Builds implementation graph from source code facts.

    Converts extracted dictionaries into typed objects and builds
    queryable ImplementationGraph (mirrors Phase 1's ArchitectureGraph).
    """

    @staticmethod
    def build_from_extracted(extracted_data: Dict, filepath: str = None) -> ImplementationGraph:
        """Build implementation graph from extracted code facts.

        Args:
            extracted_data: Dictionary with 'classes' and 'calls' from extractor
            filepath: Optional filepath for source tracking

        Returns:
            ImplementationGraph object with classes and method calls

        Raises:
            ValueError: If extracted_data format is invalid
        """
        if not isinstance(extracted_data, dict):
            raise ValueError("extracted_data must be a dictionary")

        if "classes" not in extracted_data or "calls" not in extracted_data:
            raise ValueError("extracted_data must have 'classes' and 'calls' keys")

        logger.info("Building implementation graph from extracted data")
        graph = ImplementationGraph()

        # Step 1: Add all class definitions
        for class_name, class_info in extracted_data["classes"].items():
            methods = {}

            # Convert method dicts to MethodDefinition objects
            for method_name, method_info in class_info.get("methods", {}).items():
                method = MethodDefinition(
                    name=method_name,
                    class_name=class_name,
                    line_number=method_info.get("line_number", 0)
                )
                methods[method_name] = method

            class_def = ClassDefinition(
                name=class_name,
                file_path=filepath or class_info.get("file_path", ""),
                line_number=class_info.get("line_number", 0),
                base_classes=class_info.get("base_classes", []),
                methods=methods,
                docstring=class_info.get("docstring"),
                layer=class_info.get("layer")
            )
            graph.add_class(class_def)
            logger.debug(f"Added class: {class_name}")

        # Step 2: Add all method calls
        for call_info in extracted_data.get("calls", []):
            method_call = MethodCall(
                source_class=call_info.get("source_class"),
                source_method=call_info.get("source_method"),
                target_class=call_info.get("target_class"),
                target_method=call_info.get("target_method"),
                call_type=call_info.get("call_type", "instance"),
                line_number=call_info.get("line_number", 0),
                explicit=call_info.get("explicit", True)
            )

            # Only add if both source and target classes are valid
            if method_call.source_class and method_call.target_class:
                graph.add_call(method_call)
                logger.debug(
                    f"Added call: {method_call.source_class} -> {method_call.target_class}"
                )

        logger.info(
            f"Graph built with {len(graph.classes)} classes and {len(graph.calls)} calls"
        )
        return graph

    @staticmethod
    def build_from_extractor(extractor, filepaths: List[str]) -> ImplementationGraph:
        """Build implementation graph using a PythonExtractor.

        Args:
            extractor: PythonExtractor instance
            filepaths: List of Python file paths to extract from

        Returns:
            ImplementationGraph object

        Raises:
            FileNotFoundError: If any file doesn't exist
            SyntaxError: If any file has syntax errors
        """
        logger.info(f"Building graph from {len(filepaths)} Python files")

        extracted = extractor.extract_from_files(filepaths)
        graph = CodeGraphBuilder.build_from_extracted(extracted)

        logger.info(f"Graph built successfully from {len(filepaths)} files")
        return graph

    @staticmethod
    def from_file(extractor, filepath: str) -> ImplementationGraph:
        """Convenience method to extract and build graph from single file.

        Args:
            extractor: PythonExtractor instance
            filepath: Path to single Python file

        Returns:
            ImplementationGraph object

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors
        """
        logger.info(f"Building graph from single file: {filepath}")

        extracted = extractor.extract_from_file(filepath)
        graph = CodeGraphBuilder.build_from_extracted(extracted, filepath)

        logger.info("Graph built successfully from single file")
        return graph
