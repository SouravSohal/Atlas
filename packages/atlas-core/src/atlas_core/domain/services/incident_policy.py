from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity


class IncidentPolicy:
    """Domain policy defining security and medical response dispatch rules."""

    @staticmethod
    def determine_dispatch_urgency(incident_type: IncidentType, severity: Severity) -> Severity:
        """Assess the required dispatch urgency for responders based on incident properties."""
        if incident_type == IncidentType.MEDICAL:
            return Severity.CRITICAL
        if severity == Severity.CRITICAL:
            return Severity.CRITICAL
        if incident_type == IncidentType.SECURITY and severity == Severity.HIGH:
            return Severity.CRITICAL
        return severity

    @staticmethod
    def requires_police_escalation(incident_type: IncidentType, severity: Severity) -> bool:
        """Determine if an incident requires escalation to public police responders."""
        if incident_type == IncidentType.SECURITY:
            return severity in (Severity.HIGH, Severity.CRITICAL)
        return False
