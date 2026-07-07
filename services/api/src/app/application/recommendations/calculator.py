from atlas_core.domain.enums.severity import Severity


class RecommendationPriorityCalculator:
    """Calculates the priority severity level based on stadium condition severity levels."""

    @staticmethod
    def calculate(
        crowd_density: float,
        incident_severity: Severity,
        queue_length: int,
    ) -> Severity:
        """Determines the severity (low, medium, high, critical) of a recommendation based on metrics."""
        if incident_severity == Severity.CRITICAL:
            return Severity.CRITICAL

        if crowd_density >= 0.9 and incident_severity == Severity.HIGH:
            return Severity.CRITICAL

        if queue_length >= 45:
            return Severity.CRITICAL

        if incident_severity == Severity.HIGH:
            return Severity.HIGH
        if crowd_density >= 0.75:
            return Severity.HIGH
        if queue_length >= 30:
            return Severity.HIGH

        if incident_severity == Severity.MEDIUM:
            return Severity.MEDIUM
        if crowd_density >= 0.5:
            return Severity.MEDIUM
        if queue_length >= 15:
            return Severity.MEDIUM

        return Severity.LOW
