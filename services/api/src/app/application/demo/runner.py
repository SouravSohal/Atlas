from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

import structlog
from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository

from app.application.demo.definition import ScenarioStep
from app.application.events import EventPublisher
from app.application.incidents.dtos import CreateIncidentRequest
from app.application.incidents.use_cases import CreateIncidentUseCase
from app.application.operational_state.factory import OperationalStateFactory
from app.application.recommendations.engine import RecommendationEngine

logger = structlog.get_logger()

@dataclass(frozen=True, kw_only=True)
class DemoNotificationEvent(DomainEvent):
    """Event representing a demo notification published during simulation."""
    message: str
    tick_index: int

@dataclass(frozen=True, kw_only=True)
class DemoGenericEvent(DomainEvent):
    """Generic event wrapper for arbitrary dict payloads in simulation."""
    event_data: dict[str, Any]

class ScenarioRunner:
    """Executes a single demo scenario step, updating databases and publishing events."""

    def __init__(
        self,
        state_repository: OperationalStateRepository[OperationalState],
        recommendation_repository: RecommendationRepository[Recommendation],
        create_incident_use_case: CreateIncidentUseCase,
        event_publisher: EventPublisher,
    ) -> None:
        self.state_repository = state_repository
        self.recommendation_repository = recommendation_repository
        self.create_incident_use_case = create_incident_use_case
        self.event_publisher = event_publisher
        self.recommendation_engine = RecommendationEngine()

    async def run_step(self, step: ScenarioStep) -> None:
        """Applies state changes, reports incidents, triggers rules, and dispatches events."""
        logger.info("Executing demo scenario step", tick_index=step.tick_index)

        # 1. Update Operational States
        for zone_str, density in step.operational_state_updates.items():
            zone_id = UUID(zone_str) if isinstance(zone_str, str) else zone_str
            state_entity = OperationalStateFactory.create(
                zone_id=zone_id,
                density=density,
                queue_waiting_minutes=int(density * 20)
            )
            await self.state_repository.save(state_entity)

        # 2. Report Incidents
        for inc_payload in step.incidents_to_create:
            zone_str = inc_payload["zone_id"]
            zone_id = UUID(zone_str) if isinstance(zone_str, str) else zone_str
            
            request = CreateIncidentRequest(
                incident_type=inc_payload["incident_type"],
                severity=inc_payload["severity"],
                description=inc_payload["description"],
                latitude=37.7749,
                longitude=-122.4194,
                reporter_id=UUID("00000000-0000-0000-0000-000000000000"),
                zone_id=zone_id
            )
            await self.create_incident_use_case.execute(request)

        # 3. Publish Notifications & Domain Events
        for notif in step.notifications_to_publish:
            logger.info("Demo Notification published", message=notif)
            # Publish event matching notification channel
            await self.event_publisher.publish(
                DemoNotificationEvent(
                    aggregate_id=uuid4(),
                    message=notif,
                    tick_index=step.tick_index,
                )
            )

        for ev in step.events_to_publish:
            await self.event_publisher.publish(
                DemoGenericEvent(
                    aggregate_id=uuid4(),
                    event_data=ev
                )
            )

        # 4. Trigger Recommendation Engine & save candidates
        for zone_str, density in step.operational_state_updates.items():
            recs = self.recommendation_engine.generate(
                crowd_density=density,
                incident_severity="medium",
                queue_length=int(density * 20),
                volunteer_availability=15,
                stadium_capacity=50000
            )
            for r in recs:
                await self.recommendation_repository.save(r)
