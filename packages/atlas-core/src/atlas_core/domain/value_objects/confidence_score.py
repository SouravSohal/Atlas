from dataclasses import dataclass
from functools import total_ordering

from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
@total_ordering
class ConfidenceScore(ValueObject):
    """Represents a model or prediction confidence score between 0.0 and 1.0."""

    value: float

    def __post_init__(self) -> None:
        try:
            value_float = float(self.value)
        except (TypeError, ValueError) as e:
            raise ValidationException(f"ConfidenceScore value must be a float, got {self.value}") from e

        if not (0.0 <= value_float <= 1.0):
            raise ValidationException(
                f"ConfidenceScore value must be between 0.0 and 1.0, got {self.value}"
            )
        object.__setattr__(self, "value", value_float)

    def __str__(self) -> str:
        return f"{self.value:.2f}"

    def __repr__(self) -> str:
        return f"ConfidenceScore(value={self.value})"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ConfidenceScore):
            return NotImplemented
        return self.value < other.value
