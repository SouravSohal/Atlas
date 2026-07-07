from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.repositories.base import Repository


class TaskRepository[T: BaseEntity](Repository[T]):
    """Async repository interface for Task entities."""
