from typing import Any

import structlog
from google.cloud import firestore

logger = structlog.get_logger()

class FirestoreSession:
    """Manages active read, write, and batch operations for Firestore.

    Responsibilities:
        - Get, set, update, delete document references.
        - Create and commit Firestore write batches.
    """

    def __init__(self, client: firestore.AsyncClient) -> None:
        self.client = client

    async def get(self, collection_name: str, document_id: str) -> dict[str, Any] | None:
        """Retrieves a document as a dictionary, or None if it doesn't exist."""
        doc_ref = self.client.collection(collection_name).document(document_id)
        snapshot = await doc_ref.get()
        if not snapshot.exists:
            return None
        return snapshot.to_dict()

    async def set(self, collection_name: str, document_id: str, data: dict[str, Any]) -> None:
        """Sets a document value."""
        doc_ref = self.client.collection(collection_name).document(document_id)
        await doc_ref.set(data)

    async def update(self, collection_name: str, document_id: str, data: dict[str, Any]) -> None:
        """Updates specific fields in a document."""
        doc_ref = self.client.collection(collection_name).document(document_id)
        await doc_ref.update(data)

    async def delete(self, collection_name: str, document_id: str) -> None:
        """Deletes a document."""
        doc_ref = self.client.collection(collection_name).document(document_id)
        await doc_ref.delete()

    def batch(self) -> firestore.AsyncWriteBatch:
        """Creates a new write batch."""
        return self.client.batch()
