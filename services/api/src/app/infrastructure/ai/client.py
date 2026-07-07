import structlog
from google import genai

logger = structlog.get_logger()

class AiClient:
    """Wrapper client for the google-genai Client."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required to initialize AiClient.")
        self.client = genai.Client(api_key=api_key)
        logger.info("Initialized google-genai Client")
