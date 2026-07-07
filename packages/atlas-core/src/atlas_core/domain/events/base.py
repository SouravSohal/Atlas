from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events."""

    aggregate_id: UUID
    event_id: UUID = field(default_factory=uuid4)
    event_type: str = field(default="")
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None or self.occurred_at.tzinfo != UTC:
            raise ValueError("occurred_at must be a timezone-aware UTC datetime.")
        if not self.event_type:
            object.__setattr__(self, "event_type", self.__class__.__name__)
