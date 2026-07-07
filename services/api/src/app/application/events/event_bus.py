from abc import ABC, abstractmethod
from collections.abc import Sequence

import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.dispatcher import EventDispatcher

logger = structlog.get_logger()

class EventBus(ABC):
    """Abstract interface representing the Application Event Bus (Port)."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publishes a single domain event to the event bus."""

    @abstractmethod
    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        """Publishes a sequence of domain events to the event bus."""

class InMemoryEventBus(EventBus):
    """In-memory implementation of the EventBus, delegating directly to EventDispatcher."""

    def __init__(self, dispatcher: EventDispatcher) -> None:
        self.dispatcher = dispatcher

    async def publish(self, event: DomainEvent) -> None:
        """Publishes the DomainEvent to the in-memory bus, immediately dispatching it."""
        logger.debug(
            "Publishing event to InMemoryEventBus",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
        )
        await self.dispatcher.dispatch(event)

    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        """Publishes multiple DomainEvents to the in-memory bus, immediately dispatching them."""
        logger.debug(
            "Publishing multiple events to InMemoryEventBus",
            count=len(events),
        )
        await self.dispatcher.dispatch_many(list(events))
