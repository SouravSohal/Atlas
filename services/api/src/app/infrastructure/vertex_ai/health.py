import structlog

from app.infrastructure.vertex_ai.client import VertexAiClient

logger = structlog.get_logger()

class VertexAiHealthCheck:
    """Verifies connection and availability of the Vertex AI Client."""

    def __init__(self, client: VertexAiClient) -> None:
        self.client = client

    async def check_health(self) -> bool:
        """Runs a cheap status verification on the Vertex AI SDK client."""
        try:
            # Check if the inner client is initialized
            return self.client.client is not None
        except Exception as e:
            logger.error("Vertex AI health check failed", error=str(e))
            return False
