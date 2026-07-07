from collections.abc import Sequence
from typing import Any
from uuid import UUID

import structlog
from atlas_core.domain.entities.base import BaseEntity
from google.cloud.firestore import AsyncCollectionReference, AsyncTransaction

from app.infrastructure.firestore.client import FirestoreClient
from app.infrastructure.firestore.exceptions import ConcurrencyException
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

    async def get_by_id(self, id: UUID, transaction: AsyncTransaction | None = None) -> T | None:
        """Fetches a domain entity by its document ID, optionally within a transaction."""
        doc_ref = self.collection_ref.document(str(id))

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

    async def list(self) -> Sequence[T]:
        """Retrieves all domain entities in the collection."""
        results: list[T] = []
        async for doc in self.collection_ref.stream():
            data = doc.to_dict()
            if data is not None:
                results.append(self.mapper.to_entity(doc.id, data))
        return results

    async def save(self, entity: T, transaction: AsyncTransaction | None = None) -> None:
        """Saves or updates a domain entity in Firestore with optimistic locking."""
        doc_ref = self.collection_ref.document(str(entity.id))

        if transaction is not None:
            await self._save_with_lock(doc_ref, entity, transaction)
        else:
            tx = self.client.client.transaction()
            async with tx as transactional_tx:
                await self._save_with_lock(doc_ref, entity, transactional_tx)

    async def _save_with_lock(self, doc_ref: Any, entity: T, transaction: AsyncTransaction) -> None:
        snapshot = await doc_ref.get(transaction=transaction)

        if not snapshot.exists:
            entity.version = 1
        else:
            data = snapshot.to_dict() or {}
            db_version = data.get("version", 1)
            if entity.version != db_version:
                raise ConcurrencyException(
                    f"Concurrency conflict: Entity version {entity.version} does not match database version {db_version}."
                )
            entity.version = db_version + 1

        serialized_data = self.mapper.to_document(entity)
        serialized_data["version"] = entity.version
        transaction.set(doc_ref, serialized_data)

        logger.debug(
            "Saved entity to Firestore with optimistic locking",
            collection=self.collection_name,
            entity_id=str(entity.id),
            version=entity.version,
        )

    async def delete(self, id: UUID, transaction: AsyncTransaction | None = None) -> None:
        """Deletes a document by its ID, optionally within a transaction."""
        doc_ref = self.collection_ref.document(str(id))

        if transaction is not None:
            transaction.delete(doc_ref)
        else:
            await doc_ref.delete()

        logger.debug(
            "Deleted entity from Firestore",
            collection=self.collection_name,
            entity_id=str(id),
            in_transaction=transaction is not None,
        )
