class AIException(Exception):
    """Base exception for all AI platform and orchestrator errors."""


class PromptNotFoundException(AIException):
    """Raised when a requested prompt template or version is not registered."""


class ValidationException(AIException):
    """Raised when the AI model response fails schema validation or hallucination checks."""


class ModelGatewayException(AIException):
    """Raised when there is an issue invoking the model gateway."""
