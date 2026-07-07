from atlas_core.domain.exceptions.domain_error import DomainException


class BusinessRuleViolation(DomainException):
    """Exception raised when a specific domain business rule or policy is violated."""
