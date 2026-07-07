from abc import ABC, abstractmethod


class HealthGateway(ABC):
    """Abstract interface for verifying status of downstream services and databases.

    Purpose:
        Coordinate deep health check validations for dependencies (Firestore, Firebase, etc.).

    Responsibilities:
        - Report component health status.

    Expected Lifecycle:
        Singleton.

    Failure Behavior:
        Should return health details without throwing exceptions to calling health endpoints.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> report = await health.check_health()
        >>> # report -> {"firestore": True, "gemini": True}
    """

    @abstractmethod
    async def check_health(self) -> dict[str, bool]:
        """Runs downstream checks, returning component name to status mappings."""
