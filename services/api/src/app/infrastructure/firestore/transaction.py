from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import structlog
from google.cloud import firestore
from google.cloud.firestore import AsyncTransaction

from app.infrastructure.firestore.client import FirestoreClient

logger = structlog.get_logger()

T_res = TypeVar("T_res")

class FirestoreTransaction:
    """Wrapper around Firestore AsyncTransaction to provide transaction boundaries and helpers."""

    def __init__(self, tx: AsyncTransaction) -> None:
        self.tx = tx

    async def get(self, doc_ref: Any) -> Any:
        """Gets a document snapshot within the transaction context."""
        return await doc_ref.get(transaction=self.tx)

    def set(self, doc_ref: Any, data: dict[str, Any]) -> None:
        """Sets document data in the transaction."""
        self.tx.set(doc_ref, data)

    def update(self, doc_ref: Any, data: dict[str, Any]) -> None:
        """Updates document data in the transaction."""
        self.tx.update(doc_ref, data)

    def delete(self, doc_ref: Any) -> None:
        """Deletes document in the transaction."""
        self.tx.delete(doc_ref)


class TransactionManager:
    """Manages Firestore transaction boundaries and handles automatic retry logic."""

    def __init__(self, client: FirestoreClient) -> None:
        self.client = client

    async def execute(
        self, transactional_callable: Callable[[AsyncTransaction], Awaitable[T_res]]
    ) -> T_res:
        """Executes a callable within a Firestore async transaction.

        Uses GCP Firestore's async_transactional wrapper to automatically handle retries.
        """
        transaction = self.client.client.transaction()

        @firestore.async_transactional
        async def run(tx: AsyncTransaction) -> T_res:
            return await transactional_callable(tx)

        try:
            logger.debug("Executing transaction block")
            result = await run(transaction)
            logger.debug("Transaction committed successfully")
            return result
        except Exception as e:
            logger.error("Transaction failed and was rolled back", error=str(e))
            raise e
