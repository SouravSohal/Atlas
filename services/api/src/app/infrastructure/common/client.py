import structlog

logger = structlog.get_logger()

class CommonInfrastructureClient:
    """Common client class providing shared utility configurations across adapters."""

    def __init__(self) -> None:
        logger.info("Initialized CommonInfrastructureClient")
