from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.repositories.task_repository import TaskRepository
from atlas_core.domain.value_objects.coordinates import Coordinates

from app.application.events import EventPublisher
from app.application.operational_state.exceptions import InvalidStateTransitionException
from app.application.operational_state.factory import OperationalStateFactory
from app.application.operational_state.snapshot import OperationalSnapshot
from app.application.operational_state.updater import OperationalStateUpdater

logger = structlog.get_logger()


class OperationalStateManager:
    """Orchestrates loading, modifying, and compiling the stadium operational state snapshot.

    Serves as the single source of truth for stadium operational picture compilation.
    """

    def __init__(
        self,
        state_repo: OperationalStateRepository[OperationalState],
        incident_repo: IncidentRepository[Any],
        task_repo: TaskRepository[Any],
        recommendation_repo: RecommendationRepository[Any],
        event_publisher: EventPublisher,
    ) -> None:
        self.state_repo = state_repo
        self.incident_repo = incident_repo
        self.task_repo = task_repo
        self.recommendation_repo = recommendation_repo
        self.event_publisher = event_publisher

    async def get_snapshot(self) -> OperationalSnapshot:
        """Loads and compiles the entire stadium operational picture snapshot."""
        # 1. Load active incidents (resolved = False)
        incidents = await self.incident_repo.list()
        active_incidents = [inc for inc in incidents if not inc.resolved]

        # 2. Load operational states
        states = await self.state_repo.list()
        crowd_conditions = {state.zone_id: state.density.value for state in states}
        queue_information = {state.zone_id: state.queue_estimate.waiting_minutes for state in states}

        # 3. Load active recommendations
        recs = await self.recommendation_repo.list()
        active_recs = [r for r in recs if r.status.value in ("pending", "approved")]

        # 4. Load tasks/volunteer allocation
        tasks = await self.task_repo.list()
        volunteer_allocation = {t.id: t.assigned_to_id for t in tasks if t.assigned_to_id is not None}

        # 5. Compute stadium health score
        health = 1.0
        # Deduct for active incidents based on severity
        for inc in active_incidents:
            if inc.severity.value in ("critical", "high"):
                health -= 0.15
            elif inc.severity.value == "medium":
                health -= 0.05

        # Deduct for heavy crowd density
        for density in crowd_conditions.values():
            if density > 0.8:
                health -= 0.10

        # Deduct for long queues
        for wait_mins in queue_information.values():
            if wait_mins > 20:
                health -= 0.05

        health = max(0.0, min(1.0, health))

        return OperationalSnapshot(
            active_incidents=[inc.id for inc in active_incidents],
            crowd_conditions=crowd_conditions,
            recommendations=[r.id for r in active_recs],
            volunteer_allocation=volunteer_allocation,
            queue_information=queue_information,
            stadium_health=health,
            timestamp=datetime.now(UTC),
        )

    async def update_zone_state(
        self,
        zone_id: UUID,
        density_value: float,
        queue_waiting_minutes: int,
        coordinates: Coordinates,
    ) -> OperationalSnapshot:
        """Applies direct state update, validates, increments version, publishes, and persists."""
        # 1. Validate inputs
        if not (0.0 <= density_value <= 1.0):
            raise InvalidStateTransitionException("Density value must be between 0.0 and 1.0.")
        if queue_waiting_minutes < 0:
            raise InvalidStateTransitionException("Queue waiting minutes cannot be negative.")

        # 2. Load state or create if missing
        state = await self.state_repo.get_by_id(zone_id)
        if not state:
            logger.info("Operational state not found for zone, initializing new state", zone_id=str(zone_id))
            state = OperationalStateFactory.create(
                zone_id=zone_id,
                density=density_value,
                queue_waiting_minutes=queue_waiting_minutes,
            )
        else:
            try:
                # Apply update via updater
                OperationalStateUpdater.update(state, density_value, queue_waiting_minutes, coordinates)
            except ValidationException as e:
                raise InvalidStateTransitionException(f"State transition validation failed: {e}") from e

        # 3. Persist
        await self.state_repo.save(state)

        # 4. Publish events
        events = list(state.domain_events)
        if events:
            logger.info("Publishing operational state domain events", count=len(events))
            await self.event_publisher.publish_many(events)
            state.clear_events()

        # 5. Return updated snapshot
        return await self.get_snapshot()
