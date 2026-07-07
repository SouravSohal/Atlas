from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from atlas_core.domain.events.base import DomainEvent


@dataclass(kw_only=True)
class BaseEntity:
    """Base class for all entities in the domain.

    Entities have a unique identity and their equality is defined by their ID.
    They can also record domain events.
    """

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
    domain_events: list[DomainEvent] = field(default_factory=list, init=False, compare=False)

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None or self.created_at.tzinfo != UTC:
            raise ValueError("created_at must be a timezone-aware UTC datetime.")
        if self.updated_at.tzinfo is None or self.updated_at.tzinfo != UTC:
            raise ValueError("updated_at must be a timezone-aware UTC datetime.")

    def record_event(self, event: DomainEvent) -> None:
        """Record a domain event to be dispatched later."""
        self.domain_events.append(event)

    def clear_events(self) -> None:
        """Clear all recorded domain events."""
        self.domain_events.clear()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
