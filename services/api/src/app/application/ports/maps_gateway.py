from abc import ABC, abstractmethod

from atlas_core.domain.value_objects.coordinates import Coordinates


class MapsGateway(ABC):
    """Abstract interface for routing and geospatial mapping services.

    Purpose:
        Abstract map logistics, geocoding, and distance calculations.

    Responsibilities:
        - Calculate routing distance/time between coordinates.

    Lifecycle:
        Singleton.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        - ValueError: If coordinate inputs are invalid.
        - ConnectionError: If connection to map API fails.
    """

    @abstractmethod
    async def calculate_distance_meters(self, origin: Coordinates, destination: Coordinates) -> float:
        """Calculates distance in meters between two coordinates."""

    @abstractmethod
    async def calculate_eta_seconds(self, origin: Coordinates, destination: Coordinates) -> float:
        """Calculates ETA in seconds between two coordinates."""
