from dataclasses import dataclass
from uuid import UUID

from atlas_core.domain.events.base import DomainEvent


@dataclass(frozen=True, kw_only=True)
class RecommendationApproved(DomainEvent):
    """Event raised when a generated recommendation is approved by an operator."""

    approved_by: UUID
