from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class UnitOfWork(ABC):
    """Interface/Port for the Unit of Work pattern managing transaction boundaries."""

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Starts a transaction context."""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Ends the transaction, committing on success or rolling back on exception."""

    @abstractmethod
    async def commit(self) -> None:
        """Commits the pending changes to the database."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back the transaction."""
