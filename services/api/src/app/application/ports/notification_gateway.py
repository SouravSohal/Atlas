from abc import ABC, abstractmethod
from typing import Any


class NotificationGateway(ABC):
    """Abstract interface for sending alerts and notifications.

    Purpose:
        Decouple notification delivery (SMS, Email, Push) from application logic.

    Responsibilities:
        - Dispatch messages to recipients.

    Expected Lifecycle:
        Singleton.

    Failure Behavior:
        - ConnectionError: If connection to notification provider fails.
        - ValueError: If payload or recipient metadata is invalid.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> await gateway.send_notification("user@test.com", "Alert", "Incident detected!")
    """

    @abstractmethod
    async def send_notification(
        self, recipient: str, title: str, body: str, payload: dict[str, Any] | None = None
    ) -> None:
        """Sends a notification to a specific recipient."""
