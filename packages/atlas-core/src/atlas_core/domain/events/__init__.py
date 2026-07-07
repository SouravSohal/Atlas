"""Domain events."""

from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
from atlas_core.domain.events.incident_created import IncidentCreated
from atlas_core.domain.events.recommendation_approved import RecommendationApproved
from atlas_core.domain.events.recommendation_generated import RecommendationGenerated

__all__ = [
    "CrowdDensityChanged",
    "DomainEvent",
    "IncidentCreated",
    "RecommendationApproved",
    "RecommendationGenerated",
]
