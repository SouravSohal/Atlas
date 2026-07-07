"""Domain layer containing domain models, rules, events, and repository interfaces."""

from atlas_core.domain import (
    entities,
    enums,
    events,
    exceptions,
    repositories,
    services,
    value_objects,
)
from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.entities.event import Event
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.entities.task import Task
from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.event_type import EventType
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.enums.user_role import UserRole
from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
from atlas_core.domain.events.incident_created import IncidentCreated
from atlas_core.domain.events.recommendation_approved import RecommendationApproved
from atlas_core.domain.events.recommendation_generated import RecommendationGenerated
from atlas_core.domain.exceptions.business_rule_error import BusinessRuleViolation
from atlas_core.domain.exceptions.domain_error import DomainException
from atlas_core.domain.exceptions.validation_error import ValidationException
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
from atlas_core.domain.services.crowd_policy import CrowdPolicy
from atlas_core.domain.services.incident_policy import IncidentPolicy
from atlas_core.domain.services.navigation_policy import NavigationPolicy
from atlas_core.domain.services.recommendation_policy import RecommendationPolicy
from atlas_core.domain.value_objects.base import ValueObject
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate

__all__ = [
    "BaseEntity",
    "BusinessRuleViolation",
    "ConfidenceScore",
    "Coordinates",
    "CrowdDensity",
    "CrowdDensityChanged",
    "CrowdPolicy",
    "DomainEvent",
    "DomainException",
    "Event",
    "EventRepository",
    "EventType",
    "Incident",
    "IncidentCreated",
    "IncidentPolicy",
    "IncidentRepository",
    "IncidentType",
    "NavigationPolicy",
    "OperationalState",
    "OperationalStateRepository",
    "QueueEstimate",
    "Recommendation",
    "RecommendationApproved",
    "RecommendationGenerated",
    "RecommendationPolicy",
    "RecommendationRepository",
    "RecommendationStatus",
    "Repository",
    "Severity",
    "Task",
    "TaskRepository",
    "User",
    "UserRole",
    "ValidationException",
    "ValueObject",
    "entities",
    "enums",
    "events",
    "exceptions",
    "repositories",
    "services",
    "value_objects",
]
