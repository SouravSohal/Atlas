from dataclasses import dataclass

from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity


@dataclass(frozen=True, kw_only=True)
class CrowdDensityChanged(DomainEvent):
    """Event raised when the crowd density in a specific zone changes."""

    location: Coordinates
    previous_density: CrowdDensity
    new_density: CrowdDensity
