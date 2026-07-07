from collections.abc import Sequence
from typing import Any

import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.event_bus import EventBus

logger = structlog.get_logger()

class EventPublisher:
    """Component used by application services to publish domain events to the EventBus."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def publish(self, event: DomainEvent) -> None:
        """Publishes a single DomainEvent to the EventBus."""
        logger.info(
            "Publishing domain event via publisher",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
        )
        await self.event_bus.publish(event)

    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        """Publishes a sequence of DomainEvents to the EventBus."""
        if not events:
            return

        logger.info(
            "Publishing multiple domain events via publisher",
            count=len(events),
        )
        await self.event_bus.publish_many(events)

    async def publish_from_entity(self, entity: Any) -> None:
        """Publishes all domain events from a domain entity and clears them on success."""
        events = getattr(entity, "domain_events", None)
        if not events:
            logger.debug(
                "No domain events found on entity",
                entity_type=type(entity).__name__,
            )
            return

        events_copy = list(events)
        logger.info(
            "Publishing domain events from entity",
            entity_type=type(entity).__name__,
            count=len(events_copy),
        )

        await self.publish_many(events_copy)

        clear_method = getattr(entity, "clear_events", None)
        if clear_method and callable(clear_method):
            clear_method()
            logger.debug(
                "Cleared domain events on entity",
                entity_type=type(entity).__name__,
            )
