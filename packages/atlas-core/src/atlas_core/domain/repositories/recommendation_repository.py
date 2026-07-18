from collections.abc import Sequence

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.repositories.base import Repository


class RecommendationRepository[T: BaseEntity](Repository[T]):
    """Async repository interface for Recommendation entities."""

    async def list_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        status: str | None = None,
        priority: str | None = None,
        action_type: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[Sequence[T], int]:
        """Retrieves a paginated, filtered, and sorted list of recommendations and the total count."""
        raise NotImplementedError
