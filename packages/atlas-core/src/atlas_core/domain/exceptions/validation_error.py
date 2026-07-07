from atlas_core.domain.exceptions.domain_error import DomainException


class ValidationException(DomainException):
    """Exception raised when input or model data validation fails."""
