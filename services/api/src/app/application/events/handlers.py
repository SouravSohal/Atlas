from typing import Protocol

from atlas_core.domain.events.base import DomainEvent


class EventHandler[E: DomainEvent](Protocol):
    """Generic async protocol representing a domain event handler."""

    async def handle(self, event: E) -> None:
        """Handles the domain event asynchronously."""
        ...
