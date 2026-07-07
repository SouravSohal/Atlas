from app.config import Settings
from app.infrastructure.storage.client import StorageClient
from app.infrastructure.storage.exceptions import StorageException


class StorageClientFactory:
    """Factory to initialize and create StorageClient instances."""

    @staticmethod
    def create(settings: Settings) -> StorageClient:
        """Creates a StorageClient instance using GCP project settings."""
        try:
            project_id = settings.gcp.project_id if settings.gcp else None
            return StorageClient(project_id=project_id)
        except Exception as e:
            raise StorageException(f"Failed to initialize StorageClient: {e}") from e
