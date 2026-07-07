from collections.abc import Sequence

import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.interfaces import EventBus

logger = structlog.get_logger()

class EventPublisher:
    """Component used by client code to publish domain events to the configured EventBus."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def publish(self, event: DomainEvent) -> None:
        """Publishes a single DomainEvent to the configured EventBus."""
        logger.info(
            "Publishing domain event via publisher",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
        )
        await self.event_bus.publish(event)

    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        """Publishes a sequence of DomainEvents to the configured EventBus."""
        if not events:
            return

        logger.info(
            "Publishing multiple domain events via publisher",
            count=len(events),
        )
        for event in events:
            await self.publish(event)
