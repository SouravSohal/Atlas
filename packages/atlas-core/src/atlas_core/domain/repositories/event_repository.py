from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.repositories.base import Repository


class EventRepository[T: BaseEntity](Repository[T]):
    """Async repository interface for Event entities."""
