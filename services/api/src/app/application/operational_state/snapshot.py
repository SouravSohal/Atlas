from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from atlas_core.domain.entities.operational_state import OperationalState


@dataclass(frozen=True)
class OperationalStateSnapshot:
    """Read-only snapshot of the operational state of a single stadium zone."""

    zone_id: UUID
    density: float
    queue_waiting_minutes: int
    last_updated: datetime

    @classmethod
    def from_entity(cls, entity: OperationalState) -> "OperationalStateSnapshot":
        """Instantiates a snapshot from an OperationalState domain entity."""
        return cls(
            zone_id=entity.zone_id,
            density=entity.density.value,
            queue_waiting_minutes=entity.queue_estimate.waiting_minutes,
            last_updated=entity.last_updated,
        )


@dataclass(frozen=True)
class OperationalSnapshot:
    """Immutable snapshot representing the entire operational picture of the stadium.

    Contains aggregate information across incidents, crowd density, recommendations,
    volunteer allocation, queues, and overall stadium health metrics.
    """

    active_incidents: list[UUID]
    crowd_conditions: dict[UUID, float]
    recommendations: list[UUID]
    volunteer_allocation: dict[UUID, UUID]
    queue_information: dict[UUID, int]
    stadium_health: float
    timestamp: datetime
