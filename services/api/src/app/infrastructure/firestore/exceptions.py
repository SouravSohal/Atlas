from atlas_core.domain.exceptions.domain_error import DomainException


class ConcurrencyException(DomainException):
    """Exception raised when an optimistic locking concurrency conflict is detected."""
