"""Data models for Phase 2: Code Abstraction."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import networkx as nx

@dataclass
class MethodDefinition:
    """Represents a method in a class."""
    name: str
    class_name: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None

    def __hash__(self) -> int:
        return hash((self.name, self.class_name))

@dataclass
class ClassDefinition:
    """Represents a class extracted from source code."""
    name: str
    file_path: str
    line_number: int
    base_classes: List[str] = field(default_factory=list)
    methods: Dict[str, MethodDefinition] = field(default_factory=dict)
    docstring: Optional[str] = None
    layer: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.name)

    def add_method(self, method: MethodDefinition) -> None:
        self.methods[method.name] = method

@dataclass
class MethodCall:
    """Represents a method call (dependency)."""
    source_class: str
    source_method: str
    target_class: str
    target_method: Optional[str] = None
    call_type: str = "instance"
    line_number: int = 0
    explicit: bool = True

    def __hash__(self) -> int:
        return hash((self.source_class, self.target_class, self.target_method, self.call_type))

@dataclass
class CallTrace:
    """Represents a trace of method calls."""
    calls: List[MethodCall] = field(default_factory=list)
    description: Optional[str] = None

    def add_call(self, call: MethodCall) -> None:
        self.calls.append(call)

    def __len__(self) -> int:
        return len(self.calls)

class ImplementationGraph:
    """Represents actual code implementation as a directed graph."""

    def __init__(self):
        self.classes: Dict[str, ClassDefinition] = {}
        self.calls: Set[MethodCall] = set()
        self.graph = nx.DiGraph()

    def add_class(self, class_def: ClassDefinition) -> None:
        self.classes[class_def.name] = class_def
        self.graph.add_node(class_def.name, file_path=class_def.file_path, line_number=class_def.line_number)

    def add_call(self, call: MethodCall) -> None:
        self.calls.add(call)
        self.graph.add_edge(call.source_class, call.target_class, source_method=call.source_method, target_method=call.target_method)

    def get_classes_called_by(self, class_name: str) -> Set[str]:
        if class_name not in self.graph:
            return set()
        return set(self.graph.successors(class_name))

    def get_callers_of(self, class_name: str) -> Set[str]:
        if class_name not in self.graph:
            return set()
        return set(self.graph.predecessors(class_name))

    def has_call(self, source_class: str, target_class: str) -> bool:
        return self.graph.has_edge(source_class, target_class)

    def get_all_dependencies(self) -> Set[tuple]:
        return {(call.source_class, call.target_class) for call in self.calls}

    def to_networkx(self) -> nx.DiGraph:
        return self.graph.copy()

    def __repr__(self) -> str:
        return f"ImplementationGraph(classes={len(self.classes)}, calls={len(self.calls)})"

    def __len__(self) -> int:
        return len(self.classes)
