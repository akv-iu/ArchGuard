"""Constraint checker for Phase 3: Logic Engine."""

from typing import List, Set, Tuple

from archguard.common.logger import get_logger
from archguard.phase3_logic_engine.models import Violation

logger = get_logger(__name__)


class ConstraintChecker:
    """Checks code against architectural constraints."""

    def __init__(self, architecture_graph, code_graph):
        """Initialize constraint checker.

        Args:
            architecture_graph: ArchitectureGraph from Phase 1
            code_graph: ImplementationGraph from Phase 2
        """
        self.architecture_graph = architecture_graph
        self.code_graph = code_graph
        logger.info("ConstraintChecker initialized")

    def find_violations(self) -> Set[Violation]:
        """Find all violations in the code.

        Checks each call in the code graph against the architecture graph.

        Returns:
            Set of Violation objects
        """
        logger.info("Checking constraints...")
        violations: Set[Violation] = set()

        # Get all edges in code graph
        code_edges = self.code_graph.calls if hasattr(self.code_graph, 'calls') else set()

        for call in code_edges:
            source_class = call.source_class
            target_class = call.target_class

            # Check if this call is allowed in architecture
            if not self._is_call_allowed(source_class, target_class):
                # Direct violation: call not in architecture graph
                violation = Violation(
                    type="DIRECT_VIOLATION",
                    source_class=source_class,
                    target_class=target_class,
                    violation_path=(f"{source_class} → {target_class}",),
                    line_number=getattr(call, 'line_number', 0),
                    filename=getattr(call, 'filename', ""),
                    severity="high"
                )
                violations.add(violation)

        logger.info(f"Found {len(violations)} violations")
        return violations

    def _is_call_allowed(self, source_class: str, target_class: str) -> bool:
        """Check if a call is allowed in the architecture.

        Args:
            source_class: Calling class
            target_class: Called class

        Returns:
            True if allowed, False otherwise
        """
        # Get architecture graph's NetworkX representation
        arch_graph = self.architecture_graph.to_networkx()

        # Check if there's a direct edge
        if arch_graph.has_edge(source_class, target_class):
            return True

        # Check if there's a transitive path allowed
        try:
            # If a path exists in architecture, the call is allowed
            import networkx as nx
            if nx.has_path(arch_graph, source_class, target_class):
                return True
        except (nx.NetworkXError, nx.NodeNotFound):
            pass

        return False

    def find_transitive_violations(self) -> Set[Violation]:
        """Find transitive violations (multi-hop calls).

        Returns:
            Set of Violation objects for transitive violations
        """
        violations: Set[Violation] = set()
        code_graph_nx = self.code_graph.to_networkx()

        # For each code edge, check if path is "too long"
        # (i.e., exists in code but not in architecture)
        for source_class in code_graph_nx.nodes():
            for target_class in code_graph_nx.nodes():
                if source_class == target_class:
                    continue

                # Check if code has a path
                try:
                    import networkx as nx
                    if nx.has_path(code_graph_nx, source_class, target_class):
                        # Code allows this path
                        # Check if architecture allows it
                        arch_graph = self.architecture_graph.to_networkx()
                        if not nx.has_path(arch_graph, source_class, target_class):
                            # Architecture doesn't allow it - transitive violation
                            code_path = nx.shortest_path(code_graph_nx, source_class, target_class)
                            violation = Violation(
                                type="TRANSITIVE_VIOLATION",
                                source_class=source_class,
                                target_class=target_class,
                                violation_path=tuple(" → ".join(code_path) for _ in [None]),
                                severity="medium"
                            )
                            violations.add(violation)
                except (nx.NetworkXError, nx.NodeNotFound):
                    pass

        return violations

