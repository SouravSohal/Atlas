from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from atlas_core.domain.entities.task import Task
from atlas_core.domain.enums.event_type import EventType
from google.cloud.firestore import AsyncTransaction

from app.config import Settings
from app.infrastructure.firestore import FirestoreClient
from app.infrastructure.firestore.exceptions import ConcurrencyException
from app.infrastructure.repositories import (
    FirestoreEventRepository,
    FirestoreIncidentRepository,
    FirestoreOperationalStateRepository,
    FirestoreRecommendationRepository,
    FirestoreTaskRepository,
)


@pytest.fixture
def firestore_client() -> FirestoreClient:
    with patch("google.cloud.firestore.AsyncClient"):
        return FirestoreClient(Settings())

@pytest.mark.asyncio
async def test_firestore_event_repository(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreEventRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "name": "Match 1",
        "event_type": "match.started",
        "start_time": datetime.now(UTC),
        "end_time": None,
    }
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.name == "Match 1"
    assert entity.event_type == EventType.MATCH_STARTED

@pytest.mark.asyncio
async def test_firestore_incident_repository(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreIncidentRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "incident_type": "security",
        "severity": "high",
        "description": "Intrusion",
        "location": {"latitude": 45.0, "longitude": 90.0},
        "reporter_id": "550e8400-e29b-41d4-a716-446655440001",
        "resolved": False,
        "resolved_at": None,
    }
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.description == "Intrusion"
    assert entity.location.latitude == 45.0

@pytest.mark.asyncio
async def test_firestore_task_repository(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreTaskRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "title": "Clear gate",
        "description": "Unlock exit gate A",
        "assigned_to_id": None,
        "incident_id": None,
        "completed": False,
        "completed_at": None,
    }
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.title == "Clear gate"
    assert entity.completed is False

@pytest.mark.asyncio
async def test_firestore_recommendation_repository(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreRecommendationRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "action_type": "reroute",
        "priority": "medium",
        "confidence": 0.85,
        "details": "Reroute traffic to exit B",
        "status": "pending",
        "approved_by_id": None,
        "approved_at": None,
    }
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.action_type == "reroute"
    assert entity.confidence.value == 0.85

@pytest.mark.asyncio
async def test_firestore_operational_state_repository(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreOperationalStateRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "zone_id": "550e8400-e29b-41d4-a716-446655440001",
        "density": 0.45,
        "queue_estimate": 10,
        "last_updated": datetime.now(UTC),
    }
    mock_doc.get.return_value = mock_snapshot

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.density.value == 0.45
    assert entity.queue_estimate.waiting_minutes == 10

@pytest.mark.asyncio
async def test_repository_optimistic_locking_success(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreTaskRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    # Pre-existing document in DB has version 1
    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.to_dict.return_value = {"version": 1}
    mock_doc.get.return_value = mock_snapshot

    mock_tx = MagicMock(spec=AsyncTransaction)

    # Entity to save has version 1
    task = Task(id=uuid4(), title="Test Task", description="Mock description", version=1)

    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act
        await repo.save(task, transaction=mock_tx)

    # Assert: version increments to 2
    assert task.version == 2
    mock_tx.set.assert_called_once()

@pytest.mark.asyncio
async def test_repository_optimistic_locking_conflict(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreTaskRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()

    # Pre-existing document in DB has version 2 (e.g. modified by another thread)
    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.to_dict.return_value = {"version": 2}
    mock_doc.get.return_value = mock_snapshot

    mock_tx = MagicMock(spec=AsyncTransaction)

    # Entity to save has outdated version 1
    task = Task(id=uuid4(), title="Test Task", description="Mock description", version=1)

    with patch.object(repo.collection_ref, "document", return_value=mock_doc), \
         pytest.raises(ConcurrencyException, match="Optimistic lock conflict"):
        await repo.save(task, transaction=mock_tx)


@pytest.mark.asyncio
async def test_repository_list(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreTaskRepository(firestore_client)
    
    # Mocking stream data
    mock_doc1 = MagicMock()
    mock_doc1.id = "550e8400-e29b-41d4-a716-446655440001"
    mock_doc1.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "title": "Task A",
        "description": "Desc A",
        "completed": False,
    }
    
    mock_doc2 = MagicMock()
    mock_doc2.id = "550e8400-e29b-41d4-a716-446655440002"
    mock_doc2.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "title": "Task B",
        "description": "Desc B",
        "completed": True,
    }
    
    from collections.abc import AsyncGenerator
    
    async def mock_stream_generator() -> AsyncGenerator[MagicMock, None]:
        yield mock_doc1
        yield mock_doc2

    with patch.object(repo.collection_ref, "stream", return_value=mock_stream_generator()):
        # Act
        items = await repo.list()

    # Assert
    assert len(items) == 2
    assert items[0].title == "Task A"
    assert items[1].title == "Task B"


@pytest.mark.asyncio
async def test_repository_delete(firestore_client: FirestoreClient) -> None:
    # Arrange
    repo = FirestoreTaskRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.delete = AsyncMock()
    
    with patch.object(repo.collection_ref, "document", return_value=mock_doc):
        # Act: Without transaction
        await repo.delete(UUID("550e8400-e29b-41d4-a716-446655440000"))
        mock_doc.delete.assert_called_once()

        # Act: With transaction
        mock_tx = MagicMock(spec=AsyncTransaction)
        await repo.delete(UUID("550e8400-e29b-41d4-a716-446655440000"), transaction=mock_tx)
        mock_tx.delete.assert_called_once_with(mock_doc)


@pytest.mark.asyncio
async def test_repository_transient_failure_handling(firestore_client: FirestoreClient) -> None:
    # Arrange
    from google.api_core.exceptions import ServiceUnavailable
    repo = FirestoreTaskRepository(firestore_client)
    mock_doc = MagicMock()
    mock_doc.get = AsyncMock()
    
    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.id = "550e8400-e29b-41d4-a716-446655440000"
    mock_snapshot.to_dict.return_value = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "version": 1,
        "title": "Clear gate",
        "description": "Unlock exit gate A",
        "assigned_to_id": None,
        "incident_id": None,
        "completed": False,
        "completed_at": None,
    }
    
    from typing import Any
    calls = 0
    async def get_with_fail(*args: Any, **kwargs: Any) -> MagicMock:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ServiceUnavailable("Service down")  # type: ignore[no-untyped-call]
        return mock_snapshot

    mock_doc.get.side_effect = get_with_fail

    with patch.object(repo.collection_ref, "document", return_value=mock_doc), \
         patch("app.infrastructure.firestore.retry.RetryPolicy.get_retry_decorator") as mock_decorator:
        from tenacity import retry, stop_after_attempt, wait_fixed
        mock_decorator.return_value = retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(0.01))

        # Act
        entity = await repo.get_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    # Assert
    assert entity is not None
    assert entity.title == "Clear gate"
    assert calls == 2
