from abc import ABC, abstractmethod
from typing import Any


class NotificationGateway(ABC):
    """Abstract interface for sending alerts and notifications.

    Purpose:
        Decouple notification delivery (SMS, Email, Push) from application logic.

    Responsibilities:
        - Dispatch messages to recipients.

    Lifecycle:
        Singleton.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        - ConnectionError: If connection to notification provider fails.
        - ValueError: If payload or recipient metadata is invalid.
    """

    @abstractmethod
    async def send_notification(
        self, recipient: str, title: str, body: str, payload: dict[str, Any] | None = None
    ) -> None:
        """Sends a notification to a specific recipient."""
