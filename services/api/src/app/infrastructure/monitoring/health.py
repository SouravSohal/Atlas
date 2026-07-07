from app.infrastructure.monitoring.client import MonitoringClient


class MonitoringHealthCheck:
    """Verifies that the monitoring diagnostics client is active."""

    def __init__(self, client: MonitoringClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if monitoring client is initialized."""
        return self.client is not None
