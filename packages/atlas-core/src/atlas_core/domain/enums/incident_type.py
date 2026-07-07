from enum import StrEnum


class IncidentType(StrEnum):
    """Represents the classification of stadium or tournament incidents."""

    MEDICAL = "medical"
    SECURITY = "security"
    FACILITY = "facility"
    CROWD_CONTROL = "crowd_control"
    WEATHER = "weather"
    OTHER = "other"

    def requires_immediate_dispatch(self) -> bool:
        """Returns True if the incident type defaults to needing immediate responder dispatch."""
        return self in (IncidentType.MEDICAL, IncidentType.SECURITY, IncidentType.CROWD_CONTROL)
