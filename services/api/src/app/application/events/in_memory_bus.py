import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.dispatcher import EventDispatcher
from app.application.events.interfaces import EventBus

logger = structlog.get_logger()

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
