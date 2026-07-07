from abc import ABC, abstractmethod


class HealthGateway(ABC):
    """Abstract interface for verifying status of downstream services and databases.

    Purpose:
        Coordinate deep health check validations for dependencies (Firestore, Firebase, etc.).

    Responsibilities:
        - Report component health status.

    Lifecycle:
        Singleton.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        Should return health details without throwing exceptions to calling health endpoints.
    """

    @abstractmethod
    async def check_health(self) -> dict[str, bool]:
        """Runs downstream checks, returning component name to status mappings."""
