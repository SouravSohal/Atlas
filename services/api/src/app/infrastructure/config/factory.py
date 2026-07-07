from app.config import get_settings
from app.infrastructure.config.client import ConfigClient


class ConfigClientFactory:
    """Factory to create ConfigClient instances."""

    @staticmethod
    def create() -> ConfigClient:
        """Creates a ConfigClient with current loaded application settings."""
        settings = get_settings()
        return ConfigClient(settings)
