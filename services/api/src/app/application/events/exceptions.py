class EventException(Exception):
    """Base exception for all event bus and dispatch errors."""

class DuplicateHandlerRegistrationException(EventException):
    """Raised when the same handler instance is registered multiple times for the same event."""

class EventDispatchException(EventException):
    """Raised when one or more event handlers fail during dispatch."""

    def __init__(self, message: str, exceptions: list[Exception]) -> None:
        super().__init__(message)
        self.exceptions = exceptions
