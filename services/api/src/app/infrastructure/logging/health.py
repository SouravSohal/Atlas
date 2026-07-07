from app.infrastructure.logging.client import LoggingClient


class LoggingHealthCheck:
    """Verifies that the structured logging configuration is healthy."""

    def __init__(self, client: LoggingClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if loggers are active and available."""
        return self.client.get_logger() is not None
