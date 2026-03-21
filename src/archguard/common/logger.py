"""Logging configuration for ArchGuard."""

import logging
import sys
from typing import Optional

# Define color codes for terminal output
_COLORS = {
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",      # Red
    "CRITICAL": "\033[35m",   # Magenta
    "RESET": "\033[0m",       # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with optional colors for terminal output."""

    def __init__(self, use_color: bool = True, fmt: Optional[str] = None):
        """Initialize ColoredFormatter.

        Args:
            use_color: Whether to use colored output
            fmt: Custom format string
        """
        self.use_color = use_color
        if fmt is None:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record.

        Args:
            record: The log record to format

        Returns:
            Formatted log message
        """
        if self.use_color and record.levelname in _COLORS:
            levelname_color = (
                f"{_COLORS[record.levelname]}{record.levelname}{_COLORS['RESET']}"
            )
            record.levelname = levelname_color

        return super().format(record)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get or create a logger for ArchGuard.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if logger already has handlers to avoid duplication
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Determine if we're in a terminal
        use_color = sys.stdout.isatty()

        # Create formatter
        formatter = ColoredFormatter(use_color=use_color)
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


def set_log_level(level: int) -> None:
    """Set log level for all ArchGuard loggers.

    Args:
        level: Logging level to set (e.g., logging.DEBUG, logging.INFO)
    """
    archguard_logger = logging.getLogger("archguard")
    archguard_logger.setLevel(level)

    # Update all handlers in the archguard logger
    for handler in archguard_logger.handlers:
        handler.setLevel(level)
