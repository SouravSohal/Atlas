from dataclasses import dataclass
from datetime import UTC, datetime

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.enums.event_type import EventType
from atlas_core.domain.exceptions.validation_error import ValidationException


@dataclass(kw_only=True)
class Event(BaseEntity):
    """Represents a tournament or match event in the system."""

    name: str
    event_type: EventType
    start_time: datetime
    end_time: datetime | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name.strip():
            raise ValidationException("Event name cannot be empty.")
        if self.start_time.tzinfo is None or self.start_time.tzinfo != UTC:
            raise ValidationException("Event start_time must be timezone-aware UTC.")
        if self.end_time is not None:
            if self.end_time.tzinfo is None or self.end_time.tzinfo != UTC:
                raise ValidationException("Event end_time must be timezone-aware UTC.")
            if self.end_time < self.start_time:
                raise ValidationException("Event end_time cannot be before start_time.")

    def complete(self, end_time: datetime) -> None:
        """Mark the event as completed at the given end time."""
        if end_time.tzinfo is None or end_time.tzinfo != UTC:
            raise ValidationException("Event end_time must be timezone-aware UTC.")
        if end_time < self.start_time:
            raise ValidationException("Event end_time cannot be before start_time.")
        self.end_time = end_time
        self.updated_at = datetime.now(UTC)
