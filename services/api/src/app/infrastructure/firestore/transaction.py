from collections.abc import Awaitable, Callable
from typing import TypeVar

import structlog
from google.cloud import firestore
from google.cloud.firestore import AsyncTransaction

from app.infrastructure.firestore.client import FirestoreClient

logger = structlog.get_logger()

T_res = TypeVar("T_res")

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
