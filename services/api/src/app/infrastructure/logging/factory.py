from app.infrastructure.logging.client import LoggingClient


class LoggingClientFactory:
    """Factory to create LoggingClient instances."""

    @staticmethod
    def create() -> LoggingClient:
        """Creates a LoggingClient instance."""
        return LoggingClient()
