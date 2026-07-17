import pytest
from pydantic import ValidationError

from app.config import Environment, Settings, configure_logging, get_settings
from app.config.settings import (
    ApiSettings,
    ApplicationSettings,
    LoggingSettings,
    SecuritySettings,
    DemoSettings,
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

def test_api_cors_origins_validation() -> None:
    # Act & Assert (Should parse comma-separated origins)
    config = ApiSettings(cors_origins="https://atlas.com, https://ops.atlas.com")
    assert config.cors_origins == ["https://atlas.com", "https://ops.atlas.com"]

    # Should raise validation error on wildcard '*'
    with pytest.raises(ValidationError, match="Wildcard '\\*' is not allowed"):
        ApiSettings(cors_origins="*")

    with pytest.raises(ValidationError, match="Wildcard '\\*' is not allowed"):
        ApiSettings(cors_origins=["https://atlas.com", "*"])

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


def test_settings_secret_key_placeholder_validation() -> None:
    # Verify that placeholder values for SECURITY__SECRET_KEY / JWT_SECRET raise ValidationError
    with pytest.raises(ValidationError, match="Security secret key.*cannot use insecure placeholder value"):
        Settings(security=SecuritySettings(secret_key="change-me"))


def test_settings_demo_password_missing_in_production() -> None:
    # Verify that missing demo credentials in Production environment fail validation
    with pytest.raises(ValidationError, match="Production configuration error: DEMO_PASSWORD"):
        Settings(
            app=ApplicationSettings(environment=Environment.PRODUCTION),
            demo=DemoSettings(mode=False, email="demo@atlas.com", password="")
        )


def test_settings_demo_password_placeholder_validation() -> None:
    # Verify that placeholder/insecure default values for DEMO_PASSWORD fail validation
    with pytest.raises(ValidationError, match="Demo password cannot use insecure placeholder or default value"):
        Settings(
            app=ApplicationSettings(environment=Environment.DEVELOPMENT),
            demo=DemoSettings(mode=True, email="demo@atlas.com", password="demo-secure-pass-1234")
        )


def test_environment_mapping_from_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET", "super-secret-key-that-is-very-long-and-secure")
    monkeypatch.setenv("DEMO_EMAIL", "production-demo@atlas.com")
    monkeypatch.setenv("DEMO_PASSWORD", "production-secure-demo-password-9876")
    monkeypatch.setenv("FIREBASE_WEB_API_KEY", "real-firebase-api-key")

    # Act
    settings = Settings()

    # Assert
    assert settings.app.environment == Environment.PRODUCTION


def test_api_cors_origins_mapping_from_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("API_CORS_ORIGINS", "https://frontend.com,https://api.com")

    # Act
    settings = Settings()

    # Assert
    assert settings.api.cors_origins == ["https://frontend.com", "https://api.com"]


