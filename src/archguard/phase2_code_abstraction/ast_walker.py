"""AST walker for Phase 2: Code Abstraction."""

from archguard.common.logger import get_logger

logger = get_logger(__name__)


class ASTWalker:
    """Walks Abstract Syntax Tree to extract architectural facts."""

    def __init__(self, tree_sitter_wrapper):
        """Initialize AST walker.

        Args:
            tree_sitter_wrapper: TreeSitterWrapper instance
        """
        self.wrapper = tree_sitter_wrapper
        logger.info("AST walker initialized")

    def walk(self, parse_tree):
        """Walk parse tree and extract facts.

        Args:
            parse_tree: Tree-Sitter parse tree

        Returns:
            Dictionary with extracted classes and calls
        """
        # TODO: Week 3 - Implement actual AST walking logic
        return {"classes": {}, "calls": []}
