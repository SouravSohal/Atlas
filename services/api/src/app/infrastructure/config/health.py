from app.infrastructure.config.client import ConfigClient


class ConfigHealthCheck:
    """Verifies that the configuration client is successfully initialized."""

    def __init__(self, client: ConfigClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if settings are parsed and configured."""
        return self.client.settings is not None
