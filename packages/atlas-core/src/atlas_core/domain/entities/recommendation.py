from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.events.recommendation_approved import RecommendationApproved
from atlas_core.domain.events.recommendation_generated import RecommendationGenerated
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore


@dataclass(kw_only=True)
class Recommendation(BaseEntity):
    """Represents a system logistics or routing recommendation."""

    action_type: str
    priority: Severity
    confidence: ConfidenceScore
    details: str
    status: RecommendationStatus = RecommendationStatus.PENDING
    approved_by_id: UUID | None = None
    approved_at: datetime | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.action_type.strip():
            raise ValidationException("Recommendation action_type cannot be empty.")
        if not self.details.strip():
            raise ValidationException("Recommendation details cannot be empty.")
        if self.status == RecommendationStatus.APPROVED and (
            self.approved_by_id is None or self.approved_at is None
        ):
            raise ValidationException(
                "Approved recommendations must have approved_by_id and approved_at set."
            )
        if self.approved_at is not None and (
            self.approved_at.tzinfo is None or self.approved_at.tzinfo != UTC
        ):
            raise ValidationException("Recommendation approved_at must be timezone-aware UTC.")

        # Record RecommendationGenerated event
        self.record_event(
            RecommendationGenerated(
                aggregate_id=self.id,
                action_type=self.action_type,
                priority=self.priority,
                confidence=self.confidence,
                details=self.details,
                occurred_at=self.created_at,
            )
        )

    def approve(self, operator_id: UUID) -> None:
        """Approve the recommendation."""
        if self.status != RecommendationStatus.PENDING:
            raise ValidationException("Only PENDING recommendations can be approved.")
        self.status = RecommendationStatus.APPROVED
        self.approved_by_id = operator_id
        self.approved_at = datetime.now(UTC)
        self.updated_at = self.approved_at

        # Record RecommendationApproved event
        self.record_event(
            RecommendationApproved(
                aggregate_id=self.id,
                approved_by=operator_id,
                occurred_at=self.approved_at,
            )
        )

    def reject(self) -> None:
        """Reject the recommendation."""
        if self.status != RecommendationStatus.PENDING:
            raise ValidationException("Only PENDING recommendations can be rejected.")
        self.status = RecommendationStatus.REJECTED
        self.updated_at = datetime.now(UTC)

    def execute(self) -> None:
        """Move the recommendation status to executing."""
        if self.status != RecommendationStatus.APPROVED:
            raise ValidationException("Only APPROVED recommendations can be executed.")
        self.status = RecommendationStatus.EXECUTING
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        """Complete execution of the recommendation."""
        if self.status != RecommendationStatus.EXECUTING:
            raise ValidationException("Only EXECUTING recommendations can be marked completed.")
        self.status = RecommendationStatus.COMPLETED
        self.updated_at = datetime.now(UTC)

    def fail(self) -> None:
        """Mark the recommendation as failed."""
        if self.status not in (
            RecommendationStatus.PENDING,
            RecommendationStatus.APPROVED,
            RecommendationStatus.EXECUTING,
        ):
            raise ValidationException("Terminal recommendations cannot be marked failed.")
        self.status = RecommendationStatus.FAILED
        self.updated_at = datetime.now(UTC)
