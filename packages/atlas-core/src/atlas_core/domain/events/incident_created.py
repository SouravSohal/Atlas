from dataclasses import dataclass
from uuid import UUID

from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.value_objects.coordinates import Coordinates


@dataclass(frozen=True, kw_only=True)
class IncidentCreated(DomainEvent):
    """Event raised when a new incident is created or reported in the system."""

    incident_type: IncidentType
    severity: Severity
    description: str
    location: Coordinates
    reporter_id: UUID
