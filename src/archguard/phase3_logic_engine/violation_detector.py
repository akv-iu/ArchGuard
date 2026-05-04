"""Violation detector for Phase 3: Logic Engine."""

from typing import Set

from archguard.common.logger import get_logger
from archguard.phase3_logic_engine.constraint_checker import ConstraintChecker
from archguard.phase3_logic_engine.models import Violation

logger = get_logger(__name__)


class ViolationDetector:
    """Detects and classifies architectural violations."""

    @staticmethod
    def detect(architecture_graph, code_graph) -> Set[Violation]:
        """Detect violations between architecture and code.

        Args:
            architecture_graph: ArchitectureGraph from Phase 1
            code_graph: ImplementationGraph from Phase 2

        Returns:
            Set of detected violations
        """
        logger.info("Detecting violations...")
        checker = ConstraintChecker(architecture_graph, code_graph)

        direct_violations = checker.find_violations()
        transitive_violations = checker.find_transitive_violations()
        circular_violations = checker.find_circular_violations()

        all_violations = direct_violations | transitive_violations | circular_violations

        logger.info(f"Detected {len(all_violations)} total violations")
        return all_violations

    @staticmethod
    def classify_violations(violations: Set[Violation]) -> dict:
        """Classify violations by type and severity.

        Args:
            violations: Set of Violation objects

        Returns:
            Dictionary with classification breakdown
        """
        classification = {
            "direct": [],
            "transitive": [],
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for violation in violations:
            # Classify by type
            if violation.type == "DIRECT_VIOLATION":
                classification["direct"].append(violation)
            elif violation.type == "TRANSITIVE_VIOLATION":
                classification["transitive"].append(violation)

            # Classify by severity
            if violation.severity == "critical":
                classification["critical"].append(violation)
            elif violation.severity == "high":
                classification["high"].append(violation)
            elif violation.severity == "medium":
                classification["medium"].append(violation)
            else:
                classification["low"].append(violation)

        return classification
