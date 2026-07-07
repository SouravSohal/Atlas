from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.repositories.base import Repository


class IncidentRepository[T: BaseEntity](Repository[T]):
    """Async repository interface for Incident entities."""
