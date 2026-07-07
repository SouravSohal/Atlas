from app.infrastructure.monitoring.client import MonitoringClient


class MonitoringClientFactory:
    """Factory to create MonitoringClient instances."""

    @staticmethod
    def create() -> MonitoringClient:
        """Creates a MonitoringClient instance."""
        return MonitoringClient()
