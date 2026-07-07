from enum import StrEnum


class EventType(StrEnum):
    """Represents the type of events occurring in the stadium and tournament system."""

    TOURNAMENT_STARTED = "tournament.started"
    TOURNAMENT_COMPLETED = "tournament.completed"
    MATCH_STARTED = "match.started"
    MATCH_COMPLETED = "match.completed"
    CROWD_DENSITY_ALERT = "crowd.density_alert"
    INCIDENT_REPORTED = "incident.reported"
    INCIDENT_RESOLVED = "incident.resolved"
