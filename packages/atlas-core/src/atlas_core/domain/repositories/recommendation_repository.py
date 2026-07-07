from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.repositories.base import Repository


class RecommendationRepository[T: BaseEntity](Repository[T]):
    """Async repository interface for Recommendation entities."""
