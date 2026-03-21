"""PlantUML parser for Phase 1: Symbolic Brain."""

import re
from typing import Dict, List, Optional, Set, Tuple

from archguard.common.exceptions import ParsingError
from archguard.common.logger import get_logger

logger = get_logger(__name__)


class PlantUMLParser:
    """Parser for PlantUML architecture specification files.

    This class reads PlantUML files and extracts architectural information
    including layers, classes, and their relationships.
    """

    def __init__(self):
        """Initialize the PlantUML parser."""
        self.content: Optional[str] = None
        self.lines: List[str] = []

    def parse(self, filepath: str) -> Dict:
        """Parse a PlantUML file.

        Args:
            filepath: Path to PlantUML file

        Returns:
            Dictionary containing parsed architecture data:
            {
                'layers': {...},
                'classes': {...},
                'edges': [...]
            }

        Raises:
            FileNotFoundError: If file not found
            ParsingError: If parsing fails
        """
        logger.info(f"Parsing PlantUML file: {filepath}")
        try:
            with open(filepath, "r") as f:
                self.content = f.read()
            self.lines = self.content.split("\n")
            return self._extract_architecture()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"PlantUML file not found: {filepath}") from e
        except Exception as e:
            raise ParsingError(f"Failed to parse PlantUML file: {str(e)}", filepath) from e

    def _extract_architecture(self) -> Dict:
        """Extract architecture information from parsed content.

        Returns:
            Dictionary with extracted architecture data:
            {
                'layers': {'LayerName': {'description': str, 'classes': [list]}},
                'classes': {'ClassName': {'layer': str, 'description': str}},
                'edges': [{'source': str, 'target': str, 'description': str}]
            }
        """
        logger.debug("Extracting architecture from PlantUML content")

        if not self.content:
            return {"layers": {}, "classes": {}, "edges": []}

        layers = self._extract_layers()
        classes = self._extract_classes(layers)
        edges = self._extract_edges()

        return {
            "layers": layers,
            "classes": classes,
            "edges": edges,
        }

    def _extract_layers(self) -> Dict[str, Dict]:
        """Extract layers from PlantUML content.

        Looks for package or component blocks like:
        package "LayerName" { ... }

        Returns:
            Dict with layer info: {'LayerName': {'description': str, 'classes': []}}
        """
        layers = {}

        # Pattern for package blocks
        package_pattern = r'package\s+"([^"]+)"\s*\{'
        matches = re.finditer(package_pattern, self.content, re.IGNORECASE)

        for match in matches:
            layer_name = match.group(1)
            layers[layer_name] = {
                "description": layer_name,  # Default description is the name
                "classes": [],
            }
            logger.debug(f"Extracted layer: {layer_name}")

        return layers

    def _extract_classes(self, layers: Dict[str, Dict]) -> Dict[str, Dict]:
        """Extract classes and assign them to layers.

        Looks for class declarations like:
        class ClassName

        Returns:
            Dict with class info: {'ClassName': {'layer': str, 'description': str}}
        """
        classes = {}

        # Pattern for class declarations
        class_pattern = r'class\s+(\w+)'
        matches = re.finditer(class_pattern, self.content, re.IGNORECASE)

        for match in matches:
            class_name = match.group(1)
            # Determine which layer this class belongs to
            layer = self._find_class_layer(class_name, layers)
            classes[class_name] = {
                "layer": layer,
                "description": class_name,  # Default description is the name
            }
            logger.debug(f"Extracted class: {class_name} in layer: {layer}")

        return classes

    def _find_class_layer(self, class_name: str, layers: Dict) -> Optional[str]:
        """Find which layer a class belongs to.

        Looks for the class within package blocks.

        Args:
            class_name: Name of the class to find
            layers: Dictionary of layers

        Returns:
            Layer name if found, else None
        """
        # Find the position of this class in the content
        class_pattern = rf'class\s+{re.escape(class_name)}\s*(?:\n|}})'
        match = re.search(class_pattern, self.content, re.IGNORECASE)

        if not match:
            return None

        class_pos = match.start()

        # Find the package block that contains this class
        # Look backwards for the nearest unmatched "{"
        brace_count = 0
        for i in range(class_pos - 1, -1, -1):
            if self.content[i] == "}":
                brace_count += 1
            elif self.content[i] == "{":
                brace_count -= 1
                if brace_count < 0:  # Found the opening brace
                    # Look backwards from this brace for package declaration
                    package_search = self.content[max(0, i - 200) : i]
                    package_names = re.findall(
                        r'package\s+"([^"]+)"\s*(?:\n|\s)*$',
                        package_search,
                        re.IGNORECASE | re.MULTILINE,
                    )
                    if package_names:
                        return package_names[-1]
                    break

        return None

    def _extract_edges(self) -> List[Dict]:
        """Extract dependencies/edges between classes.

        Looks for arrows like:
        ClassName --> OtherClassName : description

        Returns:
            List of edge dictionaries: [{'source': str, 'target': str, 'description': str}]
        """
        edges = []

        # Pattern for dependencies: Class1 --> Class2 : optionalDescription
        edge_pattern = r'(\w+)\s*-->\s*(\w+)(?:\s*:\s*(.+?))?(?:\n|$)'
        matches = re.finditer(edge_pattern, self.content)

        for match in matches:
            source = match.group(1)
            target = match.group(2)
            description = match.group(3) or ""
            description = description.strip()

            edges.append({
                "source": source,
                "target": target,
                "description": description,
            })
            logger.debug(f"Extracted edge: {source} --> {target}")

        return edges

