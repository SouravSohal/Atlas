from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore


class RecommendationFactory:
    """Factory to create Recommendation domain entities with confidence scores."""

    @staticmethod
    def create(
        action_type: str,
        priority: Severity,
        confidence_value: float,
        details: str,
    ) -> Recommendation:
        """Instantiates a new Recommendation entity."""
        return Recommendation(
            action_type=action_type,
            priority=priority,
            confidence=ConfidenceScore(value=confidence_value),
            details=details,
        )
