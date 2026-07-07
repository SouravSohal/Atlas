import structlog

from app.infrastructure.firestore.client import FirestoreClient

logger = structlog.get_logger()

class FirestoreHealthCheck:
    """Verifies connection and capability of the Firestore Client."""

    def __init__(self, client: FirestoreClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Evaluates whether the Firestore client can communicate successfully."""
        try:
            # Check connection state dynamically by checking active collections
            async for _ in self.client.client.collections():
                break
            return True
        except Exception as e:
            logger.error("Firestore health check failed", error=str(e))
            return False
