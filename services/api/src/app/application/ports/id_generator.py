from abc import ABC, abstractmethod
from uuid import UUID


class IdGenerator(ABC):
    """Abstract interface for generating unique identifiers.

    Purpose:
        Provide unique, standard unique IDs (e.g., UUIDv4) across the application.

    Responsibilities:
        - Generate unique identifiers.

    Expected Lifecycle:
        Singleton. Stateless.

    Failure Behavior:
        Should not raise exceptions under normal operations.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> new_id = await id_generator.generate()
    """

    @abstractmethod
    async def generate(self) -> UUID:
        """Generates a unique UUID."""
