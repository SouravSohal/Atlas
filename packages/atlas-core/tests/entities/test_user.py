import pytest

from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.user_role import UserRole
from atlas_core.domain.exceptions.validation_error import ValidationException


def test_user_creation_valid() -> None:
    # Arrange & Act
    user = User(name="John Doe", role=UserRole.FAN, email="john@example.com")

    # Assert
    assert user.name == "John Doe"
    assert user.role == UserRole.FAN
    assert user.email == "john@example.com"

def test_user_creation_invalid_name() -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValidationException, match="User name cannot be empty"):
        User(name="  ", role=UserRole.FAN, email="john@example.com")

def test_user_creation_invalid_email() -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValidationException, match="User email must be a valid email address"):
        User(name="John Doe", role=UserRole.FAN, email="invalid-email")

def test_user_update_role() -> None:
    # Arrange
    user = User(name="John Doe", role=UserRole.VOLUNTEER, email="john@example.com")

    # Act
    user.update_role(UserRole.OPERATOR)

    # Assert
    assert user.role == UserRole.OPERATOR
