from abc import ABC, abstractmethod
from uuid import UUID


class CurrentUserProvider(ABC):
    """Abstract interface for retrieving the authenticated user context.

    Purpose:
        Provide access to the identity of the user performing the current request.

    Responsibilities:
        - Retrieve current authenticated user ID.
        - Retrieve current user roles.

    Lifecycle:
        Scoped. Typically instantiated per HTTP request or task execution context.

    Thread Safety:
        Must be thread-safe within the task context (e.g. using contextvars).

    Error Expectations:
        - AttributeError: If no user is authenticated in the current context.
    """

    @abstractmethod
    async def get_user_id(self) -> UUID:
        """Retrieves the authenticated user's ID."""

    @abstractmethod
    async def get_roles(self) -> list[str]:
        """Retrieves the authenticated user's roles."""
