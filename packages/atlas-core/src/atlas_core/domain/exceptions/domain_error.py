class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
