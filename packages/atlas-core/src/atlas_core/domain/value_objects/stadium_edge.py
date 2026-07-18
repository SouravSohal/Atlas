from dataclasses import dataclass
from uuid import UUID

from atlas_core.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class StadiumEdge(ValueObject):
    """Represents an interconnected pathway between two stadium nodes."""

    source_id: UUID
    destination_id: UUID
    distance_meters: float
    avg_walk_seconds: float
    max_throughput_pax_min: float
    congestion_factor: float = 0.0
    emergency_access: bool = True
