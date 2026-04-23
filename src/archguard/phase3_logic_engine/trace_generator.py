"""Trace generator for Phase 3: Logic Engine."""

import json
from typing import Dict, List, Set

from archguard.common.logger import get_logger
from archguard.phase3_logic_engine.models import Violation, ViolationTrace, ViolationReport

logger = get_logger(__name__)


class TraceGenerator:
    """Generates structured JSON violation traces."""

    @staticmethod
    def generate_json_traces(violations: Set[Violation]) -> str:
        """Generate JSON trace from violations.

        Args:
            violations: Set of Violation objects

        Returns:
            JSON string representation of violations
        """
        logger.info(f"Generating JSON traces for {len(violations)} violations")

        # Convert to ViolationReport for structured output
        report = ViolationReport()
        for violation in violations:
            report.add_violation(violation)

        return json.dumps(report.to_dict(), indent=2, default=str)

    @staticmethod
    def generate_violation_traces(violations: Set[Violation],
                                 architecture_graph=None) -> List[ViolationTrace]:
        """Generate detailed violation traces with context.

        Args:
            violations: Set of Violation objects
            architecture_graph: Optional ArchitectureGraph for context

        Returns:
            List of ViolationTrace objects
        """
        logger.info(f"Generating violation traces for {len(violations)} violations")
        traces: List[ViolationTrace] = []

        for violation in violations:
            # Create trace with context
            trace = ViolationTrace(
                violation=violation,
                architecture_rule=TraceGenerator._get_architecture_rule(
                    violation.source_class,
                    violation.target_class,
                    architecture_graph
                ),
                suggested_fix=TraceGenerator._suggest_fix(violation)
            )
            traces.append(trace)

        return traces

    @staticmethod
    def _get_architecture_rule(source_class: str, target_class: str,
                              architecture_graph) -> str:
        """Get the architecture rule for a call.

        Args:
            source_class: Source class name
            target_class: Target class name
            architecture_graph: Architecture graph

        Returns:
            Description of architecture rule
        """
        if architecture_graph is None:
            return "No architectural rule found"

        # Try to find the direct edge
        arch_graph = architecture_graph.to_networkx()
        if arch_graph.has_edge(source_class, target_class):
            return f"Architecture allows: {source_class} → {target_class}"

        # Check for transitive path
        try:
            import networkx as nx
            if nx.has_path(arch_graph, source_class, target_class):
                path = nx.shortest_path(arch_graph, source_class, target_class)
                path_str = " → ".join(path)
                return f"Architecture allows transitive path: {path_str}"
        except (Exception,):
            pass

        return f"Architecture does not allow: {source_class} → {target_class}"

    @staticmethod
    def _suggest_fix(violation: Violation) -> str:
        """Suggest a fix for a violation.

        Args:
            violation: Violation object

        Returns:
            Suggested fix string
        """
        if violation.type == "DIRECT_VIOLATION":
            return (f"Remove the direct call from {violation.source_class} to "
                   f"{violation.target_class}, or add appropriate layer through "
                   f"architectural redesign.")
        elif violation.type == "TRANSITIVE_VIOLATION":
            return (f"Break the chain: {violation.source_class} transitively "
                   f"calls {violation.target_class}. Consider refactoring to "
                   f"follow architectural layers.")
        else:
            return f"Review and refactor to comply with architectural constraints."

    @staticmethod
    def generate_human_readable(violations: Set[Violation],
                               max_violations: int = None) -> str:
        """Generate human-readable violation report.

        Args:
            violations: Set of Violation objects
            max_violations: Max violations to include (None = all)

        Returns:
            Formatted string report
        """
        logger.info(f"Generating human-readable report for {len(violations)} violations")

        if not violations:
            return "✅ No architectural violations detected!"

        report_lines = [
            f"📋 Architectural Violation Report",
            f"{'='*50}",
            f"Total Violations: {len(violations)}",
            f"",
        ]

        # Sort violations for consistent output
        sorted_violations = sorted(violations,
                                 key=lambda v: (v.type, v.source_class, v.target_class))

        # Limit if needed
        if max_violations:
            sorted_violations = sorted_violations[:max_violations]

        for i, violation in enumerate(sorted_violations, 1):
            report_lines.append(f"Violation #{i}")
            report_lines.append(f"  Type: {violation.type}")
            report_lines.append(f"  From: {violation.source_class}")
            report_lines.append(f"  To: {violation.target_class}")
            report_lines.append(f"  Severity: {violation.severity.upper()}")
            if violation.violation_path:
                report_lines.append(f"  Path: {' → '.join(violation.violation_path)}")
            report_lines.append("")

        return "\n".join(report_lines)

