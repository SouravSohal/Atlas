from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Abstract interface for system clock operations.

    Purpose:
        Decouple the application from the system clock to allow deterministic testing
        and timezone consistency.

    Responsibilities:
        - Provide current timezone-aware timestamp.

    Lifecycle:
        Singleton. Stateless and safe to share across the application lifecycle.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        Should not raise exceptions under normal operations.
    """

    @abstractmethod
    async def now(self) -> datetime:
        """Returns the current timezone-aware datetime."""
