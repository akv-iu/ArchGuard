"""Graph builder for Phase 1: Symbolic Brain."""

from typing import Dict

import networkx as nx

from archguard.common.logger import get_logger
from archguard.phase1_symbolic_brain.models import (
    ArchitectureClass,
    ArchitectureEdge,
    ArchitectureGraph,
    Layer,
)

logger = get_logger(__name__)


class GraphBuilder:
    """Builds the architecture graph from parsed PlantUML data."""

    @staticmethod
    def build_from_parsed(architecture_data: Dict) -> ArchitectureGraph:
        """Build an ArchitectureGraph from parsed PlantUML data.

        Args:
            architecture_data: Dictionary returned from PlantUMLParser.parse()
                Expected structure:
                {
                    'layers': {'LayerName': {'description': str, 'classes': []}},
                    'classes': {'ClassName': {'layer': str, 'description': str}},
                    'edges': [{'source': str, 'target': str, 'description': str}]
                }

        Returns:
            ArchitectureGraph object representing the network of dependencies
        """
        logger.info("Building architecture graph from parsed data")
        graph = ArchitectureGraph()

        # Extract data from architecture_data
        layers_data = architecture_data.get("layers", {})
        classes_data = architecture_data.get("classes", {})
        edges_data = architecture_data.get("edges", [])

        # Step 1: Add layers to graph
        logger.debug(f"Adding {len(layers_data)} layers to graph")
        for layer_name, layer_info in layers_data.items():
            description = layer_info.get("description", layer_name)
            layer = Layer(layer_name, description)
            graph.add_layer(layer)
            logger.debug(f"Added layer: {layer_name}")

        # Step 2: Add classes to graph
        logger.debug(f"Adding {len(classes_data)} classes to graph")
        for class_name, class_info in classes_data.items():
            layer_name = class_info.get("layer")
            description = class_info.get("description", class_name)
            arch_class = ArchitectureClass(class_name, layer_name, description)
            graph.add_class(arch_class)
            logger.debug(f"Added class: {class_name} in layer: {layer_name}")

        # Step 3: Add edges (dependencies) to graph
        logger.debug(f"Adding {len(edges_data)} edges to graph")
        for edge_data in edges_data:
            source = edge_data.get("source")
            target = edge_data.get("target")
            description = edge_data.get("description", "")
            edge_type = edge_data.get("edge_type", "calls")

            edge = ArchitectureEdge(
                source,
                target,
                edge_type=edge_type,
                description=description,
            )
            graph.add_edge(edge)
            logger.debug(f"Added edge: {source} --> {target}")

        logger.info(
            f"Graph built successfully: {len(graph.layers)} layers, "
            f"{len(graph.classes)} classes, {len(graph.edges)} edges"
        )
        return graph

    @staticmethod
    def to_networkx(architecture_graph: ArchitectureGraph) -> nx.DiGraph:
        """Convert ArchitectureGraph to NetworkX DiGraph.

        Args:
            architecture_graph: ArchitectureGraph object

        Returns:
            NetworkX DiGraph representation
        """
        return architecture_graph.to_networkx()

