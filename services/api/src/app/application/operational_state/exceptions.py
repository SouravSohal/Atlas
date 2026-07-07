class OperationalStateException(Exception):
    """Base exception for all operational state manager errors."""

class StateNotFoundException(OperationalStateException):
    """Raised when the expected operational state cannot be found."""

class VersionConflictException(OperationalStateException):
    """Raised when there is a version mismatch/optimistic lock conflict."""

class InvalidStateTransitionException(OperationalStateException):
    """Raised when an update contains invalid or out-of-order data."""
