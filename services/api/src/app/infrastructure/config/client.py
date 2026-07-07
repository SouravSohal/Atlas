from typing import Any

from app.config import Settings


class ConfigClient:
    """Wrapper client for settings and configuration access."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration value dynamically by key attribute."""
        return getattr(self.settings, key, default)
