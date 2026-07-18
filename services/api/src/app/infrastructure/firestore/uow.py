from types import TracebackType
from typing import Self

from google.cloud.firestore import AsyncTransaction

from app.infrastructure.firestore.client import FirestoreClient


class FirestoreUnitOfWork:
    """Unit of Work implementation managing Firestore transactions."""

    def __init__(self, client: FirestoreClient) -> None:
        self.client = client
        self._transaction = client.client.transaction()
        self.transaction: AsyncTransaction | None = None

    async def __aenter__(self) -> Self:
        self.transaction = self._transaction
        aenter = getattr(self._transaction, "__aenter__")
        await aenter()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        aexit = getattr(self._transaction, "__aexit__")
        result = await aexit(exc_type, exc_val, exc_tb)
        self.transaction = None
        return bool(result)
