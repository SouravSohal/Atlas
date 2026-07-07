from uuid import UUID

import structlog
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.value_objects.coordinates import Coordinates

from app.application.events import EventPublisher
from app.application.operational_state.factory import OperationalStateFactory
from app.application.operational_state.snapshot import OperationalStateSnapshot
from app.application.operational_state.updater import OperationalStateUpdater

logger = structlog.get_logger()

class OperationalStateService:
    """Application Service orchestrating the retrieval and mutation of stadium zones operational states."""

    def __init__(
        self,
        repository: OperationalStateRepository[OperationalState],
        event_publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    async def get_state(self, zone_id: UUID) -> OperationalStateSnapshot | None:
        """Retrieves a read-only snapshot of the operational state for a stadium zone."""
        entity = await self.repository.get_by_id(zone_id)
        if not entity:
            return None
        return OperationalStateSnapshot.from_entity(entity)

    async def update_state(
        self,
        zone_id: UUID,
        density: float,
        queue_waiting_minutes: int,
        coordinates: Coordinates,
    ) -> OperationalStateSnapshot:
        """Updates (or creates if not exists) the zone's operational state and publishes events.

        Saves the state inside the repository and dispatches all resulting domain events.
        """
        entity = await self.repository.get_by_id(zone_id)

        if not entity:
            logger.info("Operational state not found for zone, initializing new state", zone_id=str(zone_id))
            entity = OperationalStateFactory.create(
                zone_id=zone_id,
                density=density,
                queue_waiting_minutes=queue_waiting_minutes,
            )
            await self.repository.save(entity)
        else:
            OperationalStateUpdater.update(
                state=entity,
                density_value=density,
                queue_waiting_minutes=queue_waiting_minutes,
                coordinates=coordinates,
            )
            await self.repository.save(entity)

        events = list(entity.domain_events)
        if events:
            logger.info(
                "Dispatching operational state domain events",
                zone_id=str(zone_id),
                events_count=len(events),
            )
            await self.event_publisher.publish_many(events)
            entity.clear_events()

        return OperationalStateSnapshot.from_entity(entity)
