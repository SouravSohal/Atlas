from app.config import Settings
from app.infrastructure.firestore.client import FirestoreClient


class FirestoreClientFactory:
    """Factory to create FirestoreClient instances."""

    @staticmethod
    def create(settings: Settings) -> FirestoreClient:
        """Creates a FirestoreClient instance using Settings."""
        return FirestoreClient(settings)
