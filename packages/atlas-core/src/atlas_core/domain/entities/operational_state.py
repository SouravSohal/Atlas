from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


@dataclass(kw_only=True)
class OperationalState(BaseEntity):
    """Represents the queue and crowd state of a facility/zone in the stadium."""

    zone_id: UUID
    density: CrowdDensity
    queue_estimate: QueueEstimate
    last_updated: datetime

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.last_updated.tzinfo is None or self.last_updated.tzinfo != UTC:
            raise ValidationException("OperationalState last_updated must be timezone-aware UTC.")

    def update_state(
        self,
        new_density: CrowdDensity,
        new_queue_estimate: QueueEstimate,
        location_coords: Coordinates,
    ) -> None:
        """Update the density and queue estimate, recording CrowdDensityChanged if necessary."""
        old_density = self.density
        self.density = new_density
        self.queue_estimate = new_queue_estimate
        self.last_updated = datetime.now(UTC)
        self.updated_at = self.last_updated

        if old_density != new_density:
            self.record_event(
                CrowdDensityChanged(
                    aggregate_id=self.zone_id,
                    location=location_coords,
                    previous_density=old_density,
                    new_density=new_density,
                    occurred_at=self.last_updated,
                )
            )
