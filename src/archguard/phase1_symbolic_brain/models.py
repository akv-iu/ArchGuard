"""Data models for Phase 1: Symbolic Brain."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import networkx as nx


@dataclass
class Layer:
    """Represents an architectural layer."""

    name: str
    description: Optional[str] = None
    classes: Set[str] = field(default_factory=set)

    def add_class(self, class_name: str) -> None:
        """Add a class to this layer.

        Args:
            class_name: Name of the class
        """
        self.classes.add(class_name)

    def remove_class(self, class_name: str) -> None:
        """Remove a class from this layer.

        Args:
            class_name: Name of the class
        """
        self.classes.discard(class_name)


@dataclass
class ArchitectureClass:
    """Represents a class in the architecture."""

    name: str
    layer: Optional[str] = None
    description: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make this dataclass hashable."""
        return hash(self.name)


@dataclass
class ArchitectureEdge:
    """Represents an allowed dependency between classes."""

    source: str
    target: str
    edge_type: str = "calls"  # Type of relationship (calls, inherits, etc.)
    description: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make this dataclass hashable."""
        return hash((self.source, self.target, self.edge_type))


class ArchitectureGraph:
    """Represents the complete architecture specification as a directed graph.

    This is the output of Phase 1. It serves as the source of truth for what
    dependencies are allowed in the system.
    """

    def __init__(self):
        """Initialize an empty architecture graph."""
        self.graph = nx.DiGraph()
        self.layers: Dict[str, Layer] = {}
        self.classes: Dict[str, ArchitectureClass] = {}
        self.edges: Set[ArchitectureEdge] = set()

    def add_layer(self, layer: Layer) -> None:
        """Add a layer to the architecture.

        Args:
            layer: Layer object to add
        """
        self.layers[layer.name] = layer

    def add_class(self, arch_class: ArchitectureClass) -> None:
        """Add a class to the architecture.

        Args:
            arch_class: ArchitectureClass object to add
        """
        self.classes[arch_class.name] = arch_class
        self.graph.add_node(arch_class.name, **arch_class.__dict__)

    def add_edge(self, edge: ArchitectureEdge) -> None:
        """Add an allowed edge to the architecture.

        Args:
            edge: ArchitectureEdge object to add
        """
        self.edges.add(edge)
        self.graph.add_edge(
            edge.source,
            edge.target,
            edge_type=edge.edge_type,
            description=edge.description,
            **edge.metadata,
        )

    def get_allowed_targets(self, source: str) -> Set[str]:
        """Get all classes that a source class is allowed to call.

        Args:
            source: Source class name

        Returns:
            Set of allowed target class names
        """
        return set(self.graph.successors(source))

    def is_edge_allowed(self, source: str, target: str) -> bool:
        """Check if an edge (dependency) is allowed.

        Args:
            source: Source class name
            target: Target class name

        Returns:
            True if edge is allowed, False otherwise
        """
        return self.graph.has_edge(source, target)

    def to_networkx(self) -> nx.DiGraph:
        """Export the architecture as a NetworkX DiGraph.

        Returns:
            NetworkX DiGraph object
        """
        return self.graph.copy()

    def __repr__(self) -> str:
        """String representation of the architecture."""
        return (
            f"ArchitectureGraph(layers={len(self.layers)}, "
            f"classes={len(self.classes)}, edges={len(self.edges)})"
        )
