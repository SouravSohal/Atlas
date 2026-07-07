from abc import ABC, abstractmethod
from uuid import UUID


class AuthorizationService(ABC):
    """Abstract interface for checking user roles and permissions.

    Purpose:
        Decouple authorization rules and claims checking from presentation layer.

    Responsibilities:
        - Authorize user actions based on roles or resource scopes.

    Lifecycle:
        Singleton or Scoped.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        - PermissionError: If authorization fails.
        - ValueError: If user ID is invalid.
    """

    @abstractmethod
    async def authorize(self, user_id: UUID, required_role: str) -> bool:
        """Checks if a user has the required role."""

    @abstractmethod
    async def authorize_resource(self, user_id: UUID, action: str, resource_id: str) -> bool:
        """Checks if a user is permitted to perform an action on a specific resource."""
