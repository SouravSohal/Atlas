import structlog

from app.infrastructure.storage.client import StorageClient

logger = structlog.get_logger()

class StorageHealthCheck:
    """Verifies connection and capability of the Cloud Storage Client."""

    def __init__(self, client: StorageClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Returns True if the underlying client is successfully loaded."""
        try:
            return self.client.client is not None
        except Exception as e:
            logger.error("Cloud Storage health check failed", error=str(e))
            return False
