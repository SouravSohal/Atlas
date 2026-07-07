from enum import StrEnum


class Severity(StrEnum):
    """Represents the urgency or impact level of an incident or system warning."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def level(self) -> int:
        """Returns numeric priority level (higher is more severe)."""
        mapping = {
            Severity.INFO: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }
        return mapping[self]

    def is_urgent(self) -> bool:
        """Checks if the severity warrants urgent response (HIGH or CRITICAL)."""
        return self in (Severity.HIGH, Severity.CRITICAL)
