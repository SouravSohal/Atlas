from abc import ABC, abstractmethod

from atlas_core.domain.value_objects.coordinates import Coordinates


class MapsGateway(ABC):
    """Abstract interface for routing and geospatial mapping services.

    Purpose:
        Abstract map logistics, geocoding, and distance calculations.

    Responsibilities:
        - Calculate routing distance/time between coordinates.

    Expected Lifecycle:
        Singleton.

    Failure Behavior:
        - ValueError: If coordinate inputs are invalid.
        - ConnectionError: If connection to map API fails.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> distance = await maps.calculate_distance_meters(origin, dest)
    """

    @abstractmethod
    async def calculate_distance_meters(self, origin: Coordinates, destination: Coordinates) -> float:
        """Calculates distance in meters between two coordinates."""

    @abstractmethod
    async def calculate_eta_seconds(self, origin: Coordinates, destination: Coordinates) -> float:
        """Calculates ETA in seconds between two coordinates."""
