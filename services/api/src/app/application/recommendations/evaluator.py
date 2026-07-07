from typing import NamedTuple

from atlas_core.domain.enums.severity import Severity


class EvaluationResult(NamedTuple):
    action_type: str
    confidence: float
    details: str


class RecommendationEvaluator:
    """Evaluates the state conditions to determine which action is required and its confidence."""

    @staticmethod
    def evaluate(
        crowd_density: float,
        incident_severity: Severity,
        queue_length: int,
        volunteer_availability: int,
        stadium_capacity: int,
    ) -> list[EvaluationResult]:
        results = []

        # Rule 1: Admissions suspension (Halt Entry)
        if crowd_density >= 0.95:
            results.append(
                EvaluationResult(
                    action_type="HALT_ENTRY",
                    confidence=0.98,
                    details=f"Stadium sector density is critical ({crowd_density:.1%}). Suspend admissions.",
                )
            )

        # Rule 2: Dispatch Emergency Responders
        if incident_severity in (Severity.CRITICAL, Severity.HIGH):
            confidence = 0.95 if incident_severity == Severity.CRITICAL else 0.85
            results.append(
                EvaluationResult(
                    action_type="DISPATCH_RESPONDERS",
                    confidence=confidence,
                    details=f"Severe incident of level {incident_severity.value} detected. Dispatch first responders immediately.",
                )
            )

        # Rule 3: Crowd Rerouting
        if crowd_density >= 0.8:
            results.append(
                EvaluationResult(
                    action_type="REROUTE_CROWD",
                    confidence=0.90,
                    details="Congestion detected. Reroute incoming fans to adjacent sectors.",
                )
            )

        # Rule 4: Open Gates
        if queue_length >= 25:
            confidence = 0.95 if crowd_density < 0.9 else 0.70
            results.append(
                EvaluationResult(
                    action_type="OPEN_GATES",
                    confidence=confidence,
                    details=f"Queue length of {queue_length} minutes is excessive. Open additional gates.",
                )
            )

        # Rule 5: Allocate Volunteers
        if queue_length >= 15 and volunteer_availability >= 3:
            results.append(
                EvaluationResult(
                    action_type="ALLOCATE_VOLUNTEERS",
                    confidence=0.85,
                    details=f"Queue length is high. Deploy {min(volunteer_availability, 5)} volunteers to manage lines.",
                )
            )

        return results
