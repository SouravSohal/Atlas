from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Abstract interface for system clock operations.

    Purpose:
        Decouple the application from the system clock to allow timezone consistency
        and deterministic testing.

    Responsibilities:
        - Provide current timezone-aware timestamp.

    Expected Lifecycle:
        Singleton. Stateless and safe to share across the application lifecycle.

    Failure Behavior:
        Should not raise exceptions under normal operations.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> # Inside a use case handler:
        >>> current_time = await clock.now()
    """

    @abstractmethod
    async def now(self) -> datetime:
        """Returns the current timezone-aware datetime."""
