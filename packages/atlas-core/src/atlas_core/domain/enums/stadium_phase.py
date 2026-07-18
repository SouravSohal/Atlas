from enum import StrEnum


class StadiumPhase(StrEnum):
    """Represents the operational phases of a stadium during a tournament match-day."""

    CLOSED = "closed"
    PRE_MATCH_INGRESS = "ingress"
    MATCH_ACTIVE = "match_active"
    POST_MATCH_EGRESS = "egress"
    EMERGENCY_EVACUATION = "evacuation"
