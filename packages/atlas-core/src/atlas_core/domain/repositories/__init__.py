"""Domain repositories."""

from atlas_core.domain.repositories.base import Repository
from atlas_core.domain.repositories.event_repository import EventRepository
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.operational_state_repository import (
    OperationalStateRepository,
)
from atlas_core.domain.repositories.recommendation_repository import (
    RecommendationRepository,
)
from atlas_core.domain.repositories.task_repository import TaskRepository

__all__ = [
    "EventRepository",
    "IncidentRepository",
    "OperationalStateRepository",
    "RecommendationRepository",
    "Repository",
    "TaskRepository",
]
