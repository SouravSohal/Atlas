from dataclasses import dataclass
from atlas_core.domain.value_objects.base import ValueObject

@dataclass(frozen=True)
class CrowdState(ValueObject):
    """Represents the aggregate crowd state of the stadium."""

    occupancy_percentage: float
    avg_wait_minutes: float
    peak_density_pax_m2: float
