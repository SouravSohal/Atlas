from dataclasses import dataclass

from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore


@dataclass(frozen=True, kw_only=True)
class RecommendationGenerated(DomainEvent):
    """Event raised when a new routing or operational recommendation is generated."""

    action_type: str
    priority: Severity
    confidence: ConfidenceScore
    details: str
