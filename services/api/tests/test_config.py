import pytest
from pydantic import ValidationError

from app.config import Environment, Settings, configure_logging, get_settings
from app.config.settings import (
    ApiSettings,
    ApplicationSettings,
    LoggingSettings,
    SecuritySettings,
)


def test_settings_load_defaults() -> None:
    # Act
    settings = Settings()

    # Assert
    assert settings.app.name == "ATLAS API"
    assert settings.app.environment == Environment.DEVELOPMENT
    assert not settings.app.debug
    assert settings.api.port == 8000
    assert settings.logging.level == "INFO"

def test_cached_singleton() -> None:
    # Act
    s1 = get_settings()
    s2 = get_settings()

    # Assert
    assert s1 is s2

def test_app_name_validation() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Application name cannot be empty"):
        ApplicationSettings(name="  ")

def test_api_port_validation() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
        ApiSettings(port=99999)

    with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
        ApiSettings(port=0)

def test_security_secret_validation() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Secret key cannot be empty"):
        SecuritySettings(secret_key="  ")

def test_security_expiry_validation() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Token expire minutes must be positive"):
        SecuritySettings(token_expire_minutes=0)

    with pytest.raises(ValidationError, match="Token expire minutes must be positive"):
        SecuritySettings(token_expire_minutes=-10)

def test_logging_level_validation() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Logging level must be one of"):
        LoggingSettings(level="TRACE")

def test_logging_configuration() -> None:
    # Arrange
    settings = Settings(logging=LoggingSettings(json_format=True, level="DEBUG"))

    # Act & Assert (Should configure successfully without raising exceptions)
    configure_logging(settings)
