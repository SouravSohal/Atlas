from dataclasses import dataclass
from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.entities.operational_state import OperationalState

@dataclass(kw_only=True)
class StadiumNode(BaseEntity):
    """Represents an operational area or zone in the stadium digital twin."""

    name: str
    category: str
    capacity: int
    operational_state: OperationalState
    health_score: float = 1.0
    dwell_time_seconds: float = 120.0
    ai_importance: float = 0.90
