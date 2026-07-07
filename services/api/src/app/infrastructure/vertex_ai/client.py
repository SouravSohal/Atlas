import structlog
from google import genai

logger = structlog.get_logger()

class VertexAiClient:
    """Wrapper client for the google-genai Client representing Vertex AI."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Vertex AI API key is required to initialize VertexAiClient.")
        self.client = genai.Client(api_key=api_key)
        logger.info("Initialized google-genai Client for Vertex AI")
