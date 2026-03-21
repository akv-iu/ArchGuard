"""Prompt generator for Phase 4: Neuro-Symbolic Handoff."""

from archguard.common.logger import get_logger

logger = get_logger(__name__)


class PromptGenerator:
    """Generates LLM prompts from violation traces."""

    @staticmethod
    def generate_prompt(violation_trace: dict, architecture_context: str = "") -> str:
        """Generate a detailed prompt for the LLM.

        Args:
            violation_trace: Dictionary with violation details
            architecture_context: Additional context about architecture

        Returns:
            Prompt string for Gemini API
        """
        logger.debug("Generating LLM prompt")
        # TODO: Week 5 - Implement actual prompt generation
        return ""
