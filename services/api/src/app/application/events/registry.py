from collections.abc import Callable
from typing import Any

import structlog
from atlas_core.domain.events.base import DomainEvent

from app.application.events.exceptions import DuplicateHandlerRegistrationException
from app.application.events.handlers import EventHandler

logger = structlog.get_logger()

class EventRegistry:
    """Registry mapping DomainEvent types to their registered EventHandlers."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler[Any]]] = {}

    def register[T: DomainEvent](self, event_type: type[T], handler: EventHandler[T]) -> None:
        """Registers an EventHandler for a specific DomainEvent type.

        Raises DuplicateHandlerRegistrationException if the handler is already registered.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler in self._handlers[event_type]:
            logger.warning(
                "Duplicate handler registration attempted",
                event_type=event_type.__name__,
                handler=handler.__class__.__name__,
            )
            raise DuplicateHandlerRegistrationException(
                f"Handler {handler.__class__.__name__} is already registered for {event_type.__name__}."
            )

        self._handlers[event_type].append(handler)
        logger.info(
            "Registered event handler",
            event_type=event_type.__name__,
            handler=handler.__class__.__name__,
        )

    def unregister[T: DomainEvent](self, event_type: type[T], handler: EventHandler[T]) -> None:
        """Unregisters an EventHandler from a specific DomainEvent type."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.info(
                "Unregistered event handler",
                event_type=event_type.__name__,
                handler=handler.__class__.__name__,
            )

    def get_handlers[T: DomainEvent](self, event_type: type[T]) -> list[EventHandler[T]]:
        """Retrieves all registered EventHandlers for the given DomainEvent type."""
        return list(self._handlers.get(event_type, []))

    def register_handlers(self, handlers: list[EventHandler[Any]]) -> None:
        """Automatically registers a list of EventHandlers based on class decorator metadata."""
        for handler in handlers:
            event_type = getattr(handler, "__event_type__", None)
            if event_type:
                self.register(event_type, handler)


def register_handler[T: DomainEvent](event_type: type[T]) -> Callable[[type[EventHandler[T]]], type[EventHandler[T]]]:
    """Decorator to mark an EventHandler class with its target DomainEvent type."""
    def decorator(cls: type[EventHandler[T]]) -> type[EventHandler[T]]:
        cls.__event_type__ = event_type  # type: ignore[attr-defined]
        return cls
    return decorator
