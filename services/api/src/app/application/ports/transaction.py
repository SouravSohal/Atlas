from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class Transaction(ABC):
    """Abstract interface representing a transaction context.

    Purpose:
        Define boundary operations for a database transaction.

    Responsibilities:
        - Control transaction boundaries.
        - Support async context manager protocol.

    Expected Lifecycle:
        Scoped / Transient. Created per database transaction block.

    Failure Behavior:
        - ValueError: If commit/rollback is called outside of an active transaction.
        - Exception: Database/infrastructure connection failures.

    Thread Safety:
        Not thread-safe. Must be used within a single asynchronous task/thread context.

    Usage Examples:
        >>> async with transaction as tx:
        >>>     # perform operations
        >>>     await tx.commit()
    """

    @abstractmethod
    async def commit(self) -> None:
        """Commits transaction modifications."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back transaction modifications."""

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Enters transaction context."""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Exits transaction context, committing on success or rolling back on exception."""


class TransactionManager(ABC):
    """Abstract interface for managing database transactions.

    Purpose:
        Create and coordinate database transactions.

    Responsibilities:
        - Initialize and return Transaction instances.

    Expected Lifecycle:
        Singleton.

    Failure Behavior:
        - ConnectionError: If unable to connect to the database.

    Thread Safety:
        Must be thread-safe.

    Usage Examples:
        >>> transaction = await transaction_manager.begin()
        >>> async with transaction:
        >>>     # transactional operations
        >>>     pass
    """

    @abstractmethod
    async def begin(self) -> Transaction:
        """Begins a new database transaction."""
