from atlas_core.domain.exceptions.business_rule_error import BusinessRuleViolation
from atlas_core.domain.exceptions.domain_error import DomainException
from atlas_core.domain.exceptions.validation_error import ValidationException


def test_exceptions_inheritance() -> None:
    # Arrange & Act & Assert
    domain_ex = DomainException("Domain error")
    rule_ex = BusinessRuleViolation("Rule violation")
    val_ex = ValidationException("Validation error")

    assert isinstance(domain_ex, Exception)
    assert isinstance(rule_ex, DomainException)
    assert isinstance(val_ex, DomainException)

    assert domain_ex.message == "Domain error"
    assert rule_ex.message == "Rule violation"
    assert val_ex.message == "Validation error"
