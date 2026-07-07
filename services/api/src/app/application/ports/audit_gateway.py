from abc import ABC, abstractmethod
from typing import Any


class AuditGateway(ABC):
    """Abstract interface for recording operational and compliance audit trails.

    Purpose:
        Provide immutable records of critical user and system actions.

    Responsibilities:
        - Record audit log entry.

    Expected Lifecycle:
        Singleton.

    Failure Behavior:
        - ConnectionError: If connection to audit backend fails.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> await audit.log_action("create_incident", "user-12", "incident-45")
    """

    @abstractmethod
    async def log_action(
        self, action: str, actor_id: str, resource: str, details: dict[str, Any] | None = None
    ) -> None:
        """Records an audit log entry."""
