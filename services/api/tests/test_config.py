from app.config.settings import Settings
from app.shared.logging import configure_logging


def test_settings_load() -> None:
    # Act
    settings = Settings()

    # Assert
    assert settings.app_name == "ATLAS API"
    assert settings.environment == "development"
    assert not settings.debug

def test_production_logging_config() -> None:
    # Act & Assert
    configure_logging("production")
