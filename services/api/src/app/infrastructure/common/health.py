from app.infrastructure.common.client import CommonInfrastructureClient


class CommonInfrastructureHealthCheck:
    """Verifies status of common infrastructure components."""

    def __init__(self, client: CommonInfrastructureClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if the common client is successfully loaded."""
        return self.client is not None
