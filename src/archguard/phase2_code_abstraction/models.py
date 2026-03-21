"""Data models for Phase 2: Code Abstraction."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class ClassDefinition:
    """Represents a class extracted from source code."""

    name: str
    module: str
    filepath: str
    line_number: int
    methods: Set[str] = field(default_factory=set)
    attributes: Dict[str, str] = field(default_factory=dict)
    parent_class: Optional[str] = None

    def __hash__(self) -> int:
        """Make this dataclass hashable."""
        return hash((self.name, self.module))


@dataclass
class MethodCall:
    """Represents a method call from one class to another."""

    source_class: str
    source_method: str
    target_class: str
    target_method: str
    source_file: str
    source_line: int
    call_type: str = "direct"  # direct, property, inherited, etc.

    def __hash__(self) -> int:
        """Make this dataclass hashable."""
        return hash((self.source_class, self.target_class, self.source_line))


class ImplementationGraph:
    """Represents the extracted code facts as a directed graph.

    This is the output of Phase 2. It represents what the actual code does,
    including all class definitions and method calls.
    """

    def __init__(self):
        """Initialize an empty implementation graph."""
        self.graph = nx.DiGraph()
        self.classes: Dict[str, ClassDefinition] = {}
        self.calls: Set[MethodCall] = set()

    def add_class(self, class_def: ClassDefinition) -> None:
        """Add a class definition to the graph.

        Args:
            class_def: ClassDefinition object
        """
        self.classes[class_def.name] = class_def
        self.graph.add_node(class_def.name, **class_def.__dict__)

    def add_call(self, method_call: MethodCall) -> None:
        """Add a method call to the graph.

        Args:
            method_call: MethodCall object
        """
        self.calls.add(method_call)
        self.graph.add_edge(
            method_call.source_class,
            method_call.target_class,
            call_type=method_call.call_type,
            source_method=method_call.source_method,
            target_method=method_call.target_method,
            source_file=method_call.source_file,
            source_line=method_call.source_line,
        )

    def get_outgoing_calls(self, class_name: str) -> Set[str]:
        """Get all classes that a class makes calls to.

        Args:
            class_name: Class name

        Returns:
            Set of target class names
        """
        return set(self.graph.successors(class_name))

    def get_incoming_calls(self, class_name: str) -> Set[str]:
        """Get all classes that call a given class.

        Args:
            class_name: Class name

        Returns:
            Set of source class names
        """
        return set(self.graph.predecessors(class_name))

    def to_networkx(self) -> nx.DiGraph:
        """Export as NetworkX DiGraph.

        Returns:
            NetworkX DiGraph object
        """
        return self.graph.copy()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ImplementationGraph(classes={len(self.classes)}, "
            f"calls={len(self.calls)})"
        )
