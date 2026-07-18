from abc import abstractmethod

from atlas_core.domain.entities.user import User
from atlas_core.domain.repositories.base import Repository


class UserRepository(Repository[User]):
    """Async repository interface for User entities."""

    @abstractmethod
    async def get_by_email(self, email: str) -> tuple[User, str] | None:
        """Retrieve a user and their hashed password by email."""

    @abstractmethod
    async def save_user(self, user: User, password_hash: str) -> None:
        """Save a user entity with their password hash."""
