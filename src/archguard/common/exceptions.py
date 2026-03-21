"""Custom exceptions for ArchGuard."""


class ArchGuardError(Exception):
    """Base exception for all ArchGuard errors."""

    pass


class ParsingError(ArchGuardError):
    """Raised when parsing fails (PlantUML or source code)."""

    def __init__(self, message: str, filename: str = "", line_number: int = 0):
        """Initialize ParsingError.

        Args:
            message: Error description
            filename: Name of file being parsed
            line_number: Line number where error occurred
        """
        self.filename = filename
        self.line_number = line_number
        full_message = f"{message}"
        if filename:
            full_message += f" in {filename}"
        if line_number > 0:
            full_message += f" at line {line_number}"
        super().__init__(full_message)


class ValidationError(ArchGuardError):
    """Raised when validation of parsed data fails."""

    def __init__(self, message: str, context: str = ""):
        """Initialize ValidationError.

        Args:
            message: Error description
            context: Additional context about validation failure
        """
        self.context = context
        full_message = message
        if context:
            full_message += f" ({context})"
        super().__init__(full_message)


class ExtractionError(ArchGuardError):
    """Raised when code extraction fails."""

    def __init__(self, message: str, language: str = "", filepath: str = ""):
        """Initialize ExtractionError.

        Args:
            message: Error description
            language: Programming language being processed
            filepath: File being processed
        """
        self.language = language
        self.filepath = filepath
        full_message = message
        if language:
            full_message += f" ({language})"
        if filepath:
            full_message += f" in {filepath}"
        super().__init__(full_message)


class ConstraintViolationError(ArchGuardError):
    """Raised when architecture constraints are violated."""

    def __init__(
        self,
        message: str,
        source_class: str = "",
        target_class: str = "",
        violation_type: str = "",
    ):
        """Initialize ConstraintViolationError.

        Args:
            message: Error description
            source_class: Class that violated the constraint
            target_class: Target of the violation
            violation_type: Type of violation (e.g., DIRECT_VIOLATION, TRANSITIVE)
        """
        self.source_class = source_class
        self.target_class = target_class
        self.violation_type = violation_type
        full_message = message
        if source_class and target_class:
            full_message += f" ({source_class} -> {target_class})"
        if violation_type:
            full_message += f" [{violation_type}]"
        super().__init__(full_message)


class ConfigurationError(ArchGuardError):
    """Raised when configuration is invalid."""

    pass


class APIError(ArchGuardError):
    """Raised when API calls (e.g., Gemini) fail."""

    def __init__(self, message: str, api_name: str = "", status_code: int = 0):
        """Initialize APIError.

        Args:
            message: Error description
            api_name: Name of API that failed
            status_code: HTTP status code if applicable
        """
        self.api_name = api_name
        self.status_code = status_code
        full_message = message
        if api_name:
            full_message += f" (API: {api_name})"
        if status_code > 0:
            full_message += f" [Status: {status_code}]"
        super().__init__(full_message)
