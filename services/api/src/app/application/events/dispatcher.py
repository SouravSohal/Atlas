import asyncio

import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.interfaces import EventHandler
from app.application.events.registry import EventRegistry

logger = structlog.get_logger()

class EventDispatcher:
    """Dispatches DomainEvents to their registered EventHandlers."""

    def __init__(self, registry: EventRegistry) -> None:
        self.registry = registry

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatches a DomainEvent to all registered handlers concurrently."""
        event_type = type(event)
        handlers = self.registry.get_handlers(event_type)

        if not handlers:
            logger.debug(
                "No registered handlers for event",
                event_type=event_type.__name__,
                event_id=str(event.event_id),
            )
            return

        logger.info(
            "Dispatching domain event",
            event_type=event_type.__name__,
            event_id=str(event.event_id),
            handlers_count=len(handlers),
        )

        tasks = []
        for handler in handlers:
            tasks.append(self._run_handler(handler, event))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_handler[T: DomainEvent](self, handler: EventHandler[T], event: T) -> None:
        """Executes a single event handler and logs errors safely."""
        handler_name = handler.__class__.__name__
        try:
            await handler.handle(event)
        except Exception as e:
            logger.error(
                "Error executing event handler",
                event_type=type(event).__name__,
                event_id=str(event.event_id),
                handler=handler_name,
                error=str(e),
                exc_info=True,
            )
