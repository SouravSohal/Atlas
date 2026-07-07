from app.config import Settings
from app.infrastructure.maps.client import MapsClient


class MapsClientFactory:
    """Factory to initialize and create MapsClient instances."""

    @staticmethod
    def create(settings: Settings) -> MapsClient:
        """Creates a MapsClient instance."""
        api_key = getattr(settings, "maps_api_key", None)
        return MapsClient(api_key=api_key)
