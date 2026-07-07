from dataclasses import dataclass

from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class Coordinates(ValueObject):
    """Represents geographic coordinates (Latitude and Longitude) on Earth."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValidationException(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValidationException(f"Longitude must be between -180 and 180, got {self.longitude}")

    def __str__(self) -> str:
        return f"({self.latitude:.6f}, {self.longitude:.6f})"

    def __repr__(self) -> str:
        return f"Coordinates(latitude={self.latitude}, longitude={self.longitude})"
