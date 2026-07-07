from dataclasses import dataclass
from datetime import UTC
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from atlas_core.domain.entities.base import BaseEntity
from google.cloud.firestore import AsyncTransaction

from app.config import Settings
from app.config.settings import FirestoreSettings
from app.infrastructure.firestore import (
    BaseRepository,
    CollectionMapper,
    FirestoreClient,
    FirestoreTransaction,
    FirestoreUnitOfWork,
    TransactionManager,
)


@dataclass(kw_only=True)
class MockDomainEntity(BaseEntity):
    """Test domain entity."""

    name: str = "Test"

class MockMapper(CollectionMapper[MockDomainEntity]):
    """Test entity mapper."""

    def to_document(self, entity: MockDomainEntity) -> dict[str, Any]:
        return {"id": str(entity.id), "name": entity.name}

    def to_entity(self, document_id: str, data: dict[str, Any]) -> MockDomainEntity:
        from uuid import UUID
        return MockDomainEntity(
            id=UUID(document_id),
            name=data["name"],
        )

@pytest.fixture
def mock_settings() -> Settings:
    return Settings(firestore=FirestoreSettings(emulator_host="localhost:8080"))

@pytest.fixture
def firestore_client(mock_settings: Settings) -> FirestoreClient:
    with patch("google.cloud.firestore.AsyncClient"):
        return FirestoreClient(mock_settings)

def test_firestore_client_init(firestore_client: FirestoreClient) -> None:
    # Assert
    assert firestore_client.client is not None

@pytest.mark.asyncio
async def test_firestore_client_close(firestore_client: FirestoreClient) -> None:
    # Act & Assert
    with patch.object(firestore_client.client, "close", new_callable=AsyncMock) as mock_close:
        await firestore_client.close()
        mock_close.assert_called_once()

@pytest.mark.asyncio
async def test_base_repository_get_by_id_success(firestore_client: FirestoreClient) -> None:
    # Arrange
    mapper = MockMapper()
    repo = BaseRepository(firestore_client, "test_collection", mapper)

    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {"name": "Test Entity"}
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.name == "Test Entity"
    assert str(entity.id) == "550e8400-e29b-41d4-a716-446655440000"

@pytest.mark.asyncio
async def test_base_repository_get_by_id_not_found(firestore_client: FirestoreClient) -> None:
    # Arrange
    mapper = MockMapper()
    repo = BaseRepository(firestore_client, "test_collection", mapper)

    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()
    mock_snapshot = MagicMock()
    mock_snapshot.exists = False
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440001"))

    # Assert
    assert entity is None

@pytest.mark.asyncio
async def test_base_repository_save_and_delete(firestore_client: FirestoreClient) -> None:
    # Arrange
    mapper = MockMapper()
    repo = BaseRepository(firestore_client, "test_collection", mapper)

    mock_doc = MagicMock()
    mock_doc.set = AsyncMock()
    mock_doc.delete = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = False
    mock_doc.get = AsyncMock(return_value=mock_snapshot)

    mock_tx = MagicMock(spec=AsyncTransaction)
    mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
    mock_tx.__aexit__ = AsyncMock(return_value=False)

    from uuid import uuid4
    entity = MockDomainEntity(id=uuid4(), name="Savable")

    with patch.object(repo.collection_ref, "document", return_value=mock_doc), \
         patch.object(firestore_client.client, "transaction", return_value=mock_tx):
        # Act: Save
        await repo.save(entity)
        # Assert
        mock_tx.set.assert_called_once()

        # Act: Delete
        await repo.delete(entity.id)
        # Assert
        mock_doc.delete.assert_called_once()

@pytest.mark.asyncio
async def test_base_repository_save_and_delete_with_transaction(firestore_client: FirestoreClient) -> None:
    # Arrange
    mapper = MockMapper()
    repo = BaseRepository(firestore_client, "test_collection", mapper)

    mock_doc = MagicMock()
    mock_tx = MagicMock(spec=AsyncTransaction)

    mock_snapshot = MagicMock()
    mock_snapshot.exists = False
    mock_doc.get = AsyncMock(return_value=mock_snapshot)

    from uuid import uuid4
    entity = MockDomainEntity(id=uuid4(), name="Savable")

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act: Save with transaction
        await repo.save(entity, transaction=mock_tx)
        mock_tx.set.assert_called_once_with(mock_doc, {"id": str(entity.id), "name": "Savable", "version": 1})

        # Act: Delete with transaction
        await repo.delete(entity.id, transaction=mock_tx)
        mock_tx.delete.assert_called_once_with(mock_doc)

@pytest.mark.asyncio
async def test_transaction_manager(firestore_client: FirestoreClient) -> None:
    # Arrange
    manager = TransactionManager(firestore_client)
    mock_tx = MagicMock(spec=AsyncTransaction)

    with patch.object(firestore_client.client, "transaction", return_value=mock_tx), \
         patch("google.cloud.firestore.async_transactional") as mock_decorator:
        mock_decorator.side_effect = lambda f: f

        async def tx_block(tx: AsyncTransaction) -> str:
            return "success"

        # Act
        result = await manager.execute(tx_block)

        # Assert
        assert result == "success"

@pytest.mark.asyncio
async def test_firestore_uow(firestore_client: FirestoreClient) -> None:
    # Arrange
    mock_tx = MagicMock(spec=AsyncTransaction)
    mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
    mock_tx.__aexit__ = AsyncMock(return_value=False)

    with patch.object(firestore_client.client, "transaction", return_value=mock_tx):
        # Act
        async with FirestoreUnitOfWork(firestore_client) as uow:
            assert uow.transaction is mock_tx

    # Assert
    mock_tx.__aenter__.assert_called_once()
    mock_tx.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_firestore_session_operations(firestore_client: FirestoreClient) -> None:
    # Arrange
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()
    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.to_dict.return_value = {"id": "123", "data": "value"}
    mock_doc.get.return_value = mock_snapshot

    mock_doc.set = AsyncMock()
    mock_doc.update = AsyncMock()
    mock_doc.delete = AsyncMock()

    mock_collection = MagicMock()
    mock_collection.document.return_value = mock_doc

    # Act
    with patch.object(firestore_client.client, "collection", return_value=mock_collection), \
         patch.object(firestore_client.client, "batch") as mock_batch:
        session = firestore_client.session()
        
        doc = await session.get("col", "doc-123")
        await session.set("col", "doc-123", {"data": "value"})
        await session.update("col", "doc-123", {"data": "new"})
        await session.delete("col", "doc-123")
        _ = session.batch()

        # Assert
        assert doc == {"id": "123", "data": "value"}
        mock_doc.get.assert_called_once()
        mock_doc.set.assert_called_once_with({"data": "value"})
        mock_doc.update.assert_called_once_with({"data": "new"})
        mock_doc.delete.assert_called_once()
        mock_batch.assert_called_once()


@pytest.mark.asyncio
async def test_firestore_transaction_operations() -> None:
    # Arrange
    mock_tx = MagicMock(spec=AsyncTransaction)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()
    
    tx = FirestoreTransaction(mock_tx)

    # Act
    await tx.get(mock_doc)
    tx.set(mock_doc, {"version": 1})
    tx.update(mock_doc, {"version": 2})
    tx.delete(mock_doc)

    # Assert
    mock_doc.get.assert_called_once_with(transaction=mock_tx)
    mock_tx.set.assert_called_once_with(mock_doc, {"version": 1})
    mock_tx.update.assert_called_once_with(mock_doc, {"version": 2})
    mock_tx.delete.assert_called_once_with(mock_doc)


def test_collection_resolver() -> None:
    # Arrange & Act & Assert
    from app.infrastructure.firestore import CollectionResolver
    
    assert CollectionResolver.resolve("Incident") == "incidents"
    assert CollectionResolver.resolve("OperationalState") == "operational_states"
    assert CollectionResolver.resolve("Category") == "categories"
    assert CollectionResolver.resolve("Task") == "tasks"


def test_timestamp_mapper() -> None:
    # Arrange & Act & Assert
    from datetime import datetime

    from app.infrastructure.firestore import TimestampMapper

    now_tz = datetime.now(UTC)
    now_naive = datetime.now()

    # to_datetime
    assert TimestampMapper.to_datetime(None) is None
    assert TimestampMapper.to_datetime(now_tz) == now_tz
    assert TimestampMapper.to_datetime(now_naive).tzinfo == UTC  # type: ignore[union-attr]

    # GCP Timestamp mock
    class MockGcpTimestamp:
        def to_datetime(self) -> datetime:
            return now_naive
            
    assert TimestampMapper.to_datetime(MockGcpTimestamp()) == now_naive.replace(tzinfo=UTC)

    # ISO string parsing
    iso_str = "2026-07-08T00:00:00Z"
    parsed = TimestampMapper.to_datetime(iso_str)
    assert parsed is not None
    assert parsed.year == 2026

    # to_timestamp
    assert TimestampMapper.to_timestamp(None) is None
    assert TimestampMapper.to_timestamp(now_tz) == now_tz
    assert TimestampMapper.to_timestamp(now_naive).tzinfo == UTC  # type: ignore[union-attr]


def test_optimistic_lock() -> None:
    # Arrange & Act & Assert
    from app.infrastructure.firestore import ConcurrencyException, OptimisticLockManager

    data = {"name": "test", "version": 2}
    incremented = OptimisticLockManager.increment_version(data)
    assert incremented["version"] == 3

    # Success check
    OptimisticLockManager.check_version(data, 2)
    OptimisticLockManager.check_version(None, None)

    # Failure checks
    with pytest.raises(ConcurrencyException, match="Document does not exist"):
        OptimisticLockManager.check_version(None, 1)

    with pytest.raises(ConcurrencyException, match="Expected version 5, but found 2"):
        OptimisticLockManager.check_version(data, 5)


@pytest.mark.asyncio
async def test_retry_strategy_success() -> None:
    # Arrange
    from app.infrastructure.firestore import RetryPolicy
    calls = 0

    async def sample_func() -> str:
        nonlocal calls
        calls += 1
        return "success"

    # Act
    res = await RetryPolicy.execute(sample_func)

    # Assert
    assert res == "success"
    assert calls == 1


@pytest.mark.asyncio
async def test_retry_strategy_transient_failure_retries() -> None:
    # Arrange
    from google.api_core.exceptions import ServiceUnavailable

    from app.infrastructure.firestore import RetryPolicy
    calls = 0

    async def sample_func() -> str:
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ServiceUnavailable("Temporary Service Down")  # type: ignore[no-untyped-call]
        return "success"

    # Act
    res = await RetryPolicy.execute(sample_func, min_seconds=0.01, max_seconds=0.05)

    # Assert
    assert res == "success"
    assert calls == 2

