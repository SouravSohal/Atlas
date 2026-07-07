import structlog
from atlas_core.domain.entities.base import BaseEntity
from google.cloud.firestore import AsyncCollectionReference, AsyncTransaction

from app.infrastructure.firestore.client import FirestoreClient
from app.infrastructure.firestore.mapper import CollectionMapper

logger = structlog.get_logger()

class BaseRepository[T: BaseEntity]:
    """Base generic repository containing helper methods for Google Cloud Firestore operations."""

    def __init__(
        self,
        client: FirestoreClient,
        collection_name: str,
        mapper: CollectionMapper[T],
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.mapper = mapper
        self.collection_ref: AsyncCollectionReference = client.client.collection(collection_name)

    async def get_by_id(self, entity_id: str, transaction: AsyncTransaction | None = None) -> T | None:
        """Fetches a domain entity by its document ID, optionally within a transaction."""
        doc_ref = self.collection_ref.document(entity_id)

        if transaction is not None:
            snapshot = await doc_ref.get(transaction=transaction)
        else:
            snapshot = await doc_ref.get()

        if not snapshot.exists:
            return None

        data = snapshot.to_dict()
        if data is None:
            return None

        return self.mapper.to_entity(snapshot.id, data)

    async def save(self, entity: T, transaction: AsyncTransaction | None = None) -> None:
        """Saves or updates a domain entity in Firestore, optionally within a transaction."""
        doc_ref = self.collection_ref.document(str(entity.id))
        data = self.mapper.to_document(entity)

        if transaction is not None:
            transaction.set(doc_ref, data)
        else:
            await doc_ref.set(data)

        logger.debug(
            "Saved entity to Firestore",
            collection=self.collection_name,
            entity_id=str(entity.id),
            in_transaction=transaction is not None,
        )

    async def delete(self, entity_id: str, transaction: AsyncTransaction | None = None) -> None:
        """Deletes a document by its ID, optionally within a transaction."""
        doc_ref = self.collection_ref.document(entity_id)

        if transaction is not None:
            transaction.delete(doc_ref)
        else:
            await doc_ref.delete()

        logger.debug(
            "Deleted entity from Firestore",
            collection=self.collection_name,
            entity_id=entity_id,
            in_transaction=transaction is not None,
        )
