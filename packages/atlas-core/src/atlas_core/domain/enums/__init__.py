"""Domain enums."""

from atlas_core.domain.enums.event_type import EventType
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.enums.user_role import UserRole
from atlas_core.domain.enums.stadium_phase import StadiumPhase

__all__ = [
    "EventType",
    "IncidentType",
    "RecommendationStatus",
    "Severity",
    "UserRole",
    "StadiumPhase",
]
