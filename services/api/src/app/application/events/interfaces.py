from abc import ABC, abstractmethod

from atlas_core.domain.events.base import DomainEvent


class EventHandler[E: DomainEvent](ABC):
    """Abstract base class for domain event handlers."""

    @abstractmethod
    async def handle(self, event: E) -> None:
        """Handles the domain event asynchronously."""

class EventBus(ABC):
    """Abstract interface representing the Application Event Bus (Port)."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publishes a domain event to the event bus."""
