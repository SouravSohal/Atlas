from app.config import Settings
from app.infrastructure.vertex_ai.client import VertexAiClient
from app.infrastructure.vertex_ai.exceptions import VertexAiException


class VertexAiClientFactory:
    """Factory to initialize and create VertexAiClient instances."""

    @staticmethod
    def create(settings: Settings) -> VertexAiClient:
        """Creates a VertexAiClient instance using Gemini settings."""
        try:
            api_key = settings.gemini.api_key
            if not api_key:
                raise ValueError("Gemini/Vertex AI API key is not configured in settings.")
            return VertexAiClient(api_key=api_key)
        except Exception as e:
            raise VertexAiException(f"Failed to initialize VertexAiClient: {e}") from e
