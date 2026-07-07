from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore


class RecommendationPolicy:
    """Domain policy governing recommendations lifecycle and auto-approvals."""

    AUTO_APPROVE_CONFIDENCE_THRESHOLD = 0.9

    @staticmethod
    def should_auto_approve(priority: Severity, confidence: ConfidenceScore) -> bool:
        """Determine if a recommendation should be auto-approved based on priority and confidence."""
        if priority == Severity.CRITICAL:
            return False
        return confidence.value >= RecommendationPolicy.AUTO_APPROVE_CONFIDENCE_THRESHOLD

    @staticmethod
    def is_valid_transition(
        current: RecommendationStatus, next_status: RecommendationStatus
    ) -> bool:
        """Validate state transition for a Recommendation status."""
        transitions = {
            RecommendationStatus.PENDING: {
                RecommendationStatus.APPROVED,
                RecommendationStatus.REJECTED,
                RecommendationStatus.FAILED,
            },
            RecommendationStatus.APPROVED: {
                RecommendationStatus.EXECUTING,
                RecommendationStatus.FAILED,
            },
            RecommendationStatus.EXECUTING: {
                RecommendationStatus.COMPLETED,
                RecommendationStatus.FAILED,
            },
            RecommendationStatus.REJECTED: set(),
            RecommendationStatus.COMPLETED: set(),
            RecommendationStatus.FAILED: set(),
        }
        return next_status in transitions.get(current, set())
