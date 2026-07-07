from app.infrastructure.maps.client import MapsClient


class MapsHealthCheck:
    """Verifies that the Google Maps client is loaded."""

    def __init__(self, client: MapsClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if maps client instance exists."""
        return self.client is not None
