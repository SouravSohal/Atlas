from datetime import UTC, datetime
from uuid import UUID

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


class OperationalStateFactory:
    """Factory for creating new OperationalState domain entities."""

    @staticmethod
    def create(
        zone_id: UUID,
        density: float = 0.0,
        queue_waiting_minutes: int = 0,
    ) -> OperationalState:
        """Creates a fresh, timezone-aware OperationalState entity using zone_id as the primary identity."""
        now = datetime.now(UTC)
        return OperationalState(
            id=zone_id,
            zone_id=zone_id,
            density=CrowdDensity(value=density),
            queue_estimate=QueueEstimate(waiting_minutes=queue_waiting_minutes),
            last_updated=now,
            created_at=now,
            updated_at=now,
        )
