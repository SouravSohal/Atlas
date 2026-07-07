from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.enums.severity import Severity

from app.application.recommendations.calculator import RecommendationPriorityCalculator
from app.application.recommendations.evaluator import RecommendationEvaluator
from app.application.recommendations.factory import RecommendationFactory
from app.application.recommendations.validator import RecommendationValidator


class RecommendationEngine:
    """Ties the validator, evaluator, calculator, and factory together to generate recommendations."""

    def __init__(self) -> None:
        self.validator = RecommendationValidator()
        self.evaluator = RecommendationEvaluator()
        self.calculator = RecommendationPriorityCalculator()
        self.factory = RecommendationFactory()

    def generate(
        self,
        crowd_density: float,
        incident_severity: str | Severity,
        queue_length: int,
        volunteer_availability: int,
        stadium_capacity: int,
    ) -> list[Recommendation]:
        """Generates Recommendation entities based on input metrics."""
        self.validator.validate_generation_params(
            crowd_density=crowd_density,
            incident_severity=incident_severity,
            queue_length=queue_length,
            volunteer_availability=volunteer_availability,
            stadium_capacity=stadium_capacity,
        )

        severity_enum = (
            Severity(incident_severity)
            if isinstance(incident_severity, str)
            else incident_severity
        )

        candidates = self.evaluator.evaluate(
            crowd_density=crowd_density,
            incident_severity=severity_enum,
            queue_length=queue_length,
            volunteer_availability=volunteer_availability,
            stadium_capacity=stadium_capacity,
        )

        priority = self.calculator.calculate(
            crowd_density=crowd_density,
            incident_severity=severity_enum,
            queue_length=queue_length,
        )

        recommendations = []
        for candidate in candidates:
            recommendation = self.factory.create(
                action_type=candidate.action_type,
                priority=priority,
                confidence_value=candidate.confidence,
                details=candidate.details,
            )
            recommendations.append(recommendation)

        return recommendations
