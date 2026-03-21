"""Global constants for ArchGuard."""

# Supported languages
SUPPORTED_LANGUAGES = ["python"]
PLANNED_LANGUAGES = ["java", "go", "rust", "typescript"]

# Violation types
VIOLATION_TYPES = {
    "DIRECT_VIOLATION": "Direct call to prohibited class",
    "TRANSITIVE_VIOLATION": "Call through prohibited intermediate class",
    "LAYER_BYPASS": "Skipping required architectural layer",
    "CIRCULAR_DEPENDENCY": "Circular dependency detected",
}

# Log levels
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}

# Default configuration
DEFAULT_CONFIG = {
    "max_trace_depth": 10,
    "timeout_seconds": 300,
    "max_violations": 1000,
    "include_transitive": True,
}
