"""Graph builder for Phase 1: Symbolic Brain."""

from typing import Dict

import networkx as nx

from archguard.common.logger import get_logger
from archguard.phase1_symbolic_brain.models import ArchitectureGraph

logger = get_logger(__name__)


class GraphBuilder:
    """Builds the architecture graph from parsed PlantUML data."""

    @staticmethod
    def build_from_parsed(architecture_data: Dict) -> ArchitectureGraph:
        """Build an ArchitectureGraph from parsed PlantUML data.

        Args:
            architecture_data: Dictionary returned from PlantUMLParser.parse()

        Returns:
            ArchitectureGraph object representing the network of dependencies
        """
        logger.info("Building architecture graph from parsed data")
        graph = ArchitectureGraph()

        # Placeholder implementation
        # TODO: Week 2 - Implement actual graph building logic
        # - Add layers from architecture_data['layers']
        # - Add classes from architecture_data['classes']
        # - Add edges from architecture_data['edges']

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
