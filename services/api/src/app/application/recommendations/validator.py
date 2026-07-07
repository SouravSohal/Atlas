from atlas_core.domain.enums.severity import Severity

from app.application.operational_state.exceptions import InvalidStateTransitionException


class RecommendationValidator:
    """Validates parameters and recommendation attributes against business policies."""

    @staticmethod
    def validate_generation_params(
        crowd_density: float,
        incident_severity: str | Severity,
        queue_length: int,
        volunteer_availability: int,
        stadium_capacity: int,
    ) -> None:
        """Validates that parameters for generating recommendation are in correct ranges."""
        if not (0.0 <= crowd_density <= 1.0):
            raise InvalidStateTransitionException("Crowd density must be between 0.0 and 1.0.")
        if queue_length < 0:
            raise InvalidStateTransitionException("Queue length cannot be negative.")
        if volunteer_availability < 0:
            raise InvalidStateTransitionException("Volunteer availability cannot be negative.")
        if stadium_capacity <= 0:
            raise InvalidStateTransitionException("Stadium capacity must be positive.")

        if isinstance(incident_severity, str):
            try:
                Severity(incident_severity)
            except ValueError as e:
                raise InvalidStateTransitionException(f"Invalid severity value: {incident_severity}") from e
