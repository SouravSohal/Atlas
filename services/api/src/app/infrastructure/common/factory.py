from app.infrastructure.common.client import CommonInfrastructureClient


class CommonInfrastructureClientFactory:
    """Factory to create CommonInfrastructureClient instances."""

    @staticmethod
    def create() -> CommonInfrastructureClient:
        """Creates a CommonInfrastructureClient."""
        return CommonInfrastructureClient()
