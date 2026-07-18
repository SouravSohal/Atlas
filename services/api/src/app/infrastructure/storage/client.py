import structlog
import google.cloud.storage as storage

logger = structlog.get_logger()

class StorageClient:
    """Wrapper client for Google Cloud Storage client operations."""

    def __init__(self, project_id: str | None = None) -> None:
        kwargs = {}
        if project_id:
            kwargs["project"] = project_id
        self.client = storage.Client(**kwargs)
        logger.info("Initialized Google Cloud Storage Client")
