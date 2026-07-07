from dataclasses import dataclass
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
