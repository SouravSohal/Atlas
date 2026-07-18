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

def test_user_can_access_security_zone() -> None:
    # Arrange
    fan = User(name="Fan User", role=UserRole.FAN, email="fan@example.com")
    athlete = User(name="Athlete User", role=UserRole.ATHLETE, email="athlete@example.com")
    volunteer = User(name="Volunteer User", role=UserRole.VOLUNTEER, email="vol@example.com")
    commander = User(name="Commander User", role=UserRole.OPERATIONS_COMMANDER, email="commander@example.com")

    # Act & Assert
    assert fan.can_access_security_zone("general_stands") is True
    assert fan.can_access_security_zone("pitch") is False

    assert athlete.can_access_security_zone("pitch") is True
    assert athlete.can_access_security_zone("locker_room") is True
    assert athlete.can_access_security_zone("vip_lounge") is False

    assert volunteer.can_access_security_zone("general_stands") is True
    assert volunteer.can_access_security_zone("pitch") is False
    assert volunteer.can_access_security_zone("vip_lounge") is False

    assert commander.can_access_security_zone("pitch") is True
    assert commander.can_access_security_zone("vip_lounge") is True
    assert commander.can_access_security_zone("locker_room") is True
