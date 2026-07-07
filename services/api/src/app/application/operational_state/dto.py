from dataclasses import dataclass
from uuid import UUID

from atlas_core.domain.events.base import DomainEvent


@dataclass(frozen=True, kw_only=True)
class GateStatusChanged(DomainEvent):
    """Event raised when the status of a stadium gate changes."""
    gate_id: UUID
    status: str  # e.g., "open", "closed"

@dataclass(frozen=True, kw_only=True)
class VolunteerAssigned(DomainEvent):
    """Event raised when a volunteer is assigned to a task."""
    task_id: UUID
    volunteer_id: UUID

@dataclass(frozen=True)
class OperationalStateUpdateDTO:
    """DTO representing an update to a zone's operational state."""
    zone_id: UUID
    density: float
    queue_waiting_minutes: int
