from enum import StrEnum


class RecommendationStatus(StrEnum):
    """Represents the lifecycle state of system-generated logistics or routing recommendations."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

    def is_terminal(self) -> bool:
        """Checks if the status is in a terminal state (cannot transition further)."""
        return self in (RecommendationStatus.COMPLETED, RecommendationStatus.FAILED, RecommendationStatus.REJECTED)
