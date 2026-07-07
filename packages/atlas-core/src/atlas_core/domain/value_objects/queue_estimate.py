from dataclasses import dataclass
from functools import total_ordering

from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
@total_ordering
class QueueEstimate(ValueObject):
    """Represents estimated waiting time in minutes."""

    waiting_minutes: int

    def __post_init__(self) -> None:
        if self.waiting_minutes < 0:
            raise ValidationException(
                f"QueueEstimate waiting minutes must be non-negative, got {self.waiting_minutes}"
            )

    def __str__(self) -> str:
        return f"{self.waiting_minutes} min"

    def __repr__(self) -> str:
        return f"QueueEstimate(waiting_minutes={self.waiting_minutes})"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, QueueEstimate):
            return NotImplemented
        return self.waiting_minutes < other.waiting_minutes
