import asyncio
from collections.abc import Sequence
from typing import Any

import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.exceptions import EventDispatchException
from app.application.events.registry import EventRegistry

logger = structlog.get_logger()

class EventDispatcher:
    """Dispatches DomainEvents to their registered EventHandlers concurrently."""

    def __init__(self, registry: EventRegistry) -> None:
        self.registry = registry

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatches a single DomainEvent to all registered handlers concurrently.

        Uses asyncio.TaskGroup to execute handlers in parallel. Collects and raises
        any exceptions raised during execution.
        """
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

        exceptions: list[Exception] = []

        async def run_handler(handler: Any) -> None:
            try:
                await handler.handle(event)
            except Exception as e:
                logger.error(
                    "Error executing event handler",
                    event_type=event_type.__name__,
                    event_id=str(event.event_id),
                    handler=handler.__class__.__name__,
                    error=str(e),
                    exc_info=True,
                )
                exceptions.append(e)

        # Execute all handlers in parallel using TaskGroup
        async with asyncio.TaskGroup() as tg:
            for handler in handlers:
                tg.create_task(run_handler(handler))

        if exceptions:
            raise EventDispatchException(
                f"Failed to dispatch event {event_type.__name__}: {len(exceptions)} handler(s) failed.",
                exceptions,
            )

    async def dispatch_many(self, events: Sequence[DomainEvent]) -> None:
        """Dispatches multiple DomainEvents sequentially, ensuring ordering guarantees."""
        all_exceptions: list[Exception] = []
        for event in events:
            try:
                await self.dispatch(event)
            except EventDispatchException as ede:
                all_exceptions.extend(ede.exceptions)
            except Exception as e:
                all_exceptions.append(e)

        if all_exceptions:
            raise EventDispatchException(
                f"Failed to dispatch multiple events: {len(all_exceptions)} handler(s) failed.",
                all_exceptions,
            )
