from abc import ABC, abstractmethod
from uuid import UUID


class IdGenerator(ABC):
    """Abstract interface for generating unique identifiers.

    Purpose:
        Provide unique, standard unique IDs (e.g., UUIDv4) across the application.

    Responsibilities:
        - Generate unique identifiers.

    Lifecycle:
        Singleton. Stateless.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        Should not raise exceptions under normal operations.
    """

    @abstractmethod
    async def generate(self) -> UUID:
        """Generates a unique UUID."""
