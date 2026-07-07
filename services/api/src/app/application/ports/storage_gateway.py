from abc import ABC, abstractmethod


class StorageGateway(ABC):
    """Abstract interface for cloud file/blob storage operations.

    Purpose:
        Decouple cloud object storage (e.g. GCS, S3) from application logic.

    Responsibilities:
        - Upload file bytes to storage buckets.
        - Generate public or signed download links.
        - Delete stored files.

    Expected Lifecycle:
        Singleton.

    Failure Behavior:
        - FileNotFoundError: If requested file doesn't exist.
        - ConnectionError: If cloud connection fails.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> url = await storage.upload("my-bucket", "image.jpg", image_bytes)
    """

    @abstractmethod
    async def upload(
        self, bucket_name: str, object_name: str, data: bytes, content_type: str | None = None
    ) -> str:
        """Uploads file bytes and returns the stored public/signed URL."""

    @abstractmethod
    async def download(self, bucket_name: str, object_name: str) -> bytes:
        """Downloads file bytes from storage."""

    @abstractmethod
    async def delete(self, bucket_name: str, object_name: str) -> None:
        """Deletes file from storage."""
