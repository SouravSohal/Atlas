from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.events.incident_created import IncidentCreated
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.coordinates import Coordinates


@dataclass(kw_only=True)
class Incident(BaseEntity):
    """Represents a stadium security or medical incident."""

    incident_type: IncidentType
    severity: Severity
    description: str
    location: Coordinates
    reporter_id: UUID
    resolved: bool = False
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.description.strip():
            raise ValidationException("Incident description cannot be empty.")
        if self.resolved_at is not None:
            if self.resolved_at.tzinfo is None or self.resolved_at.tzinfo != UTC:
                raise ValidationException("Incident resolved_at must be timezone-aware UTC.")
            if not self.resolved:
                raise ValidationException("Incident resolved_at cannot be set if incident is not resolved.")

        # Record IncidentCreated event
        self.record_event(
            IncidentCreated(
                aggregate_id=self.id,
                incident_type=self.incident_type,
                severity=self.severity,
                description=self.description,
                location=self.location,
                reporter_id=self.reporter_id,
                occurred_at=self.created_at,
            )
        )

    def resolve(self) -> None:
        """Resolve the incident."""
        self.resolved = True
        self.resolved_at = datetime.now(UTC)
        self.updated_at = self.resolved_at

    def update_severity(self, new_severity: Severity) -> None:
        """Update the severity of the incident."""
        self.severity = new_severity
        self.updated_at = datetime.now(UTC)
