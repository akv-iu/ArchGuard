"""Constraint checker for Phase 3: Logic Engine."""

import networkx as nx
from typing import Set

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
        """Find all direct violations in the code.

        A direct violation is any implementation edge (u, v) where no direct
        edge (u, v) exists in the architecture graph.

        Returns:
            Set of Violation objects
        """
        logger.info("Checking constraints...")
        violations: Set[Violation] = set()

        code_edges = self.code_graph.calls if hasattr(self.code_graph, 'calls') else set()

        for call in code_edges:
            source_class = call.source_class
            target_class = call.target_class

            if not self._is_call_allowed(source_class, target_class):
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

        logger.info(f"Found {len(violations)} direct violations")
        return violations

    def _is_call_allowed(self, source_class: str, target_class: str) -> bool:
        """Check if a direct call is permitted by the architecture.

        Only a direct edge in the architecture graph constitutes permission.
        Transitive reachability does NOT count — that is the definition of a
        layer bypass violation.

        Args:
            source_class: Calling class
            target_class: Called class

        Returns:
            True only if a direct architecture edge (source, target) exists
        """
        return self.architecture_graph.is_edge_allowed(source_class, target_class)

    def find_transitive_violations(self) -> Set[Violation]:
        """Find transitive violations — multi-hop paths in code that reach a
        class not directly reachable from the source in the architecture.

        Uses nx.descendants() per node (O(V·(V+E))) instead of iterating all
        node pairs (O(V²·(V+E))).

        Returns:
            Set of Violation objects for transitive violations
        """
        violations: Set[Violation] = set()
        code_graph_nx = self.code_graph.to_networkx()
        arch_graph = self.architecture_graph.to_networkx()

        for source in code_graph_nx.nodes():
            for target in nx.descendants(code_graph_nx, source):
                if source == target:
                    continue
                # Pairs with a direct code edge are already covered by find_violations
                if code_graph_nx.has_edge(source, target):
                    continue
                # Find the shortest path in code between this pair
                code_path = nx.shortest_path(code_graph_nx, source, target)
                # Only flag if the path contains at least one forbidden hop.
                # A path where every hop is arch-permitted is architecturally sound;
                # flagging it would produce spurious violations on conforming code.
                path_has_forbidden_hop = any(
                    not arch_graph.has_edge(code_path[i], code_path[i + 1])
                    for i in range(len(code_path) - 1)
                )
                if path_has_forbidden_hop:
                    violation = Violation(
                        type="TRANSITIVE_VIOLATION",
                        source_class=source,
                        target_class=target,
                        violation_path=tuple(code_path),
                        severity="medium"
                    )
                    violations.add(violation)

        logger.info(f"Found {len(violations)} transitive violations")
        return violations

    def find_circular_violations(self) -> Set[Violation]:
        """Find circular dependency violations in the implementation graph.

        Uses nx.simple_cycles() to detect cycles. Each distinct cycle is
        reported as one CIRCULAR_DEPENDENCY violation.

        Returns:
            Set of Violation objects for circular dependencies
        """
        violations: Set[Violation] = set()
        code_graph_nx = self.code_graph.to_networkx()

        for cycle in nx.simple_cycles(code_graph_nx):
            if len(cycle) < 2:
                continue
            cycle_path = tuple(cycle) + (cycle[0],)
            violation = Violation(
                type="CIRCULAR_DEPENDENCY",
                source_class=cycle[0],
                target_class=cycle[-1],
                violation_path=cycle_path,
                severity="critical"
            )
            violations.add(violation)

        logger.info(f"Found {len(violations)} circular violations")
        return violations
