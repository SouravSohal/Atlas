import structlog

from app.infrastructure.firebase.client import FirebaseClient

logger = structlog.get_logger()

class FirebaseHealthCheck:
    """Verifies that the Firebase Admin SDK client is active."""

    def __init__(self, client: FirebaseClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if the Firebase app reference is successfully initialized."""
        try:
            return self.client.app is not None
        except Exception as e:
            logger.error("Firebase health check failed", error=str(e))
            return False
