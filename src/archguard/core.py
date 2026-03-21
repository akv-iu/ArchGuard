"""Core orchestrator for ArchGuard - Main facade integrating all 4 phases."""

from typing import Dict, List, Optional, Tuple

from archguard.common.logger import get_logger

logger = get_logger(__name__)


class ArchGuard:
    """Main orchestrator class for ArchGuard neuro-symbolic referee.

    This class provides the high-level interface to the entire ArchGuard pipeline,
    connecting all four phases:
    1. Symbolic Brain (PlantUML → Architecture Graph)
    2. Code Abstraction (Source Code → Implementation Graph)
    3. Logic Engine (Constraint Satisfaction & Violation Detection)
    4. Neuro-Symbolic Handoff (JSON → Gemini → Natural Language)

    Attributes:
        architecture_graph: Loaded architecture specification as NetworkX DiGraph
        code_graph: Extracted code facts as NetworkX DiGraph
    """

    def __init__(self):
        """Initialize ArchGuard orchestrator."""
        self.architecture_graph = None
        self.code_graph = None
        logger.info("ArchGuard orchestrator initialized")

    def load_architecture(self, architecture_path: str) -> None:
        """Load and parse architecture specification from PlantUML file.

        This method implements Phase 1: Symbolic Brain.

        Args:
            architecture_path: Path to PlantUML architecture file

        Raises:
            FileNotFoundError: If architecture file not found
            ParsingError: If PlantUML parsing fails
        """
        logger.info(f"Loading architecture from {architecture_path}")
        # Phase 1 implementation will go here
        # Will use PlantUMLParser and GraphBuilder
        pass

    def analyze(
        self,
        code_path: str,
        explain: bool = False,
        api_key: Optional[str] = None,
    ) -> Tuple[List[Dict], Optional[List[Dict]]]:
        """Analyze source code against loaded architecture.

        This method orchestrates Phases 2, 3, and optionally 4.

        Args:
            code_path: Path to source code file or directory
            explain: Whether to use Gemini API for LLM explanations
            api_key: API key for Gemini (required if explain=True)

        Returns:
            Tuple of (violations, explanations)
            - violations: List of violation dictionaries
            - explanations: List of explanation dictionaries (None if explain=False)

        Raises:
            FileNotFoundError: If code file not found
            ExtractionError: If code extraction fails
            APIError: If LLM API call fails and explain=True
        """
        logger.info(f"Analyzing code at {code_path}")

        # Phase 2: Code Abstraction
        # Will extract classes and calls using Tree-Sitter
        logger.info("Phase 2: Extracting implementation facts...")
        # code_graph = CodeGraphBuilder.build(code_path)

        # Phase 3: Logic Engine
        # Will check constraints and generate violations
        logger.info("Phase 3: Detecting architectural violations...")
        # violations = ConstraintChecker.check(architecture_graph, code_graph)

        # Phase 4 (Optional): Neuro-Symbolic Handoff
        if explain and api_key:
            logger.info("Phase 4: Generating natural language explanations...")
            # explanations = GeminiClient.explain(violations, api_key)
            # return violations, explanations
            pass

        return [], None

    def export_violations(self, output_path: str, violations: List[Dict]) -> None:
        """Export violations to JSON file.

        Args:
            output_path: Path where JSON should be written
            violations: List of violation dictionaries
        """
        logger.info(f"Exporting violations to {output_path}")
        # Will implement JSON serialization
        pass

    def export_architecture(self, output_path: str) -> None:
        """Export loaded architecture graph to file.

        Args:
            output_path: Path where graph should be written
        """
        logger.info(f"Exporting architecture graph to {output_path}")
        # Will implement graph serialization
        pass


def main():
    """Main entry point for ArchGuard CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ArchGuard: Neuro-Symbolic Referee for Architectural Drift Detection"
    )
    parser.add_argument(
        "--architecture",
        required=True,
        help="Path to PlantUML architecture specification",
    )
    parser.add_argument(
        "--code",
        required=True,
        help="Path to source code file or directory to analyze",
    )
    parser.add_argument(
        "--output",
        default="violations.json",
        help="Output path for violations JSON (default: violations.json)",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Use Gemini API to generate natural language explanations",
    )
    parser.add_argument(
        "--api-key",
        help="Google Gemini API key (required if --explain is used)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        import logging
        from archguard.common.logger import set_log_level

        set_log_level(logging.DEBUG)

    # Initialize and run ArchGuard
    referee = ArchGuard()
    referee.load_architecture(args.architecture)
    violations, explanations = referee.analyze(args.code, args.explain, args.api_key)
    referee.export_violations(args.output, violations)

    print(f"Analysis complete. {len(violations)} violations found.")
    if explanations:
        print("Explanations generated using Gemini API.")


if __name__ == "__main__":
    main()
