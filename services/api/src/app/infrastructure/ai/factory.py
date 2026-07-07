from app.config import Settings
from app.infrastructure.ai.client import AiClient
from app.infrastructure.ai.exceptions import AiException


class AiClientFactory:
    """Factory to initialize and create AiClient instances."""

    @staticmethod
    def create(settings: Settings) -> AiClient:
        """Creates an AiClient instance using Gemini settings."""
        try:
            api_key = settings.gemini.api_key
            if not api_key:
                raise ValueError("Gemini API key is not configured in settings.")
            return AiClient(api_key=api_key)
        except Exception as e:
            raise AiException(f"Failed to initialize AiClient: {e}") from e
