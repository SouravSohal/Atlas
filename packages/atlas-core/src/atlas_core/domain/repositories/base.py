from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from atlas_core.domain.entities.base import BaseEntity


class Repository[T: BaseEntity](ABC):
    """Generic base repository interface defining standard async CRUD operations."""

    @abstractmethod
    async def save(self, entity: T) -> None:
        """Persist or update the entity.

        Args:
            entity: The entity instance to save.
        """

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        """Retrieve an entity by its unique identifier.

        Args:
            id: The unique identifier of the entity.

        Returns:
            The entity instance if found, otherwise None.
        """

    @abstractmethod
    async def list(self) -> Sequence[T]:
        """Retrieve all instances of the entity.

        Returns:
            A sequence of entity instances.
        """

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Remove an entity by its unique identifier.

        Args:
            id: The unique identifier of the entity to delete.
        """
