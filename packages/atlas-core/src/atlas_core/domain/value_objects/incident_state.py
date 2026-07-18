from dataclasses import dataclass

from atlas_core.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class IncidentState(ValueObject):
    """Represents the aggregate incident alert state of the stadium."""

    active_count: int
    critical_count: int
    warning_count: int
