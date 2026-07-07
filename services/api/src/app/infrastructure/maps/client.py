import structlog

logger = structlog.get_logger()

class MapsClient:
    """Wrapper client for the Google Maps API operations."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        logger.info("Initialized Google Maps Client")
