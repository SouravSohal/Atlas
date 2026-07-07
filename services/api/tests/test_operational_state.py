from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.value_objects.coordinates import Coordinates

from app.application.events import EventPublisher
from app.application.operational_state import (
    OperationalStateFactory,
    OperationalStateService,
    OperationalStateSnapshot,
    OperationalStateUpdater,
)


def test_operational_state_factory() -> None:
    # Arrange
    zone_id = uuid4()

    # Act
    entity = OperationalStateFactory.create(zone_id, density=0.75, queue_waiting_minutes=15)

    # Assert
    assert entity.id == zone_id
    assert entity.zone_id == zone_id
    assert entity.density.value == 0.75
    assert entity.queue_estimate.waiting_minutes == 15
    assert isinstance(entity.last_updated, datetime)

def test_operational_state_updater() -> None:
    # Arrange
    zone_id = uuid4()
    entity = OperationalStateFactory.create(zone_id, density=0.25, queue_waiting_minutes=5)
    coords = Coordinates(latitude=34.0, longitude=-118.0)

    # Act
    OperationalStateUpdater.update(entity, density_value=0.5, queue_waiting_minutes=10, coordinates=coords)

    # Assert
    assert entity.density.value == 0.5
    assert entity.queue_estimate.waiting_minutes == 10
    # There should be a CrowdDensityChanged domain event recorded
    assert len(entity.domain_events) == 1

def test_operational_state_snapshot() -> None:
    # Arrange
    zone_id = uuid4()
    entity = OperationalStateFactory.create(zone_id, density=0.8, queue_waiting_minutes=20)

    # Act
    snapshot = OperationalStateSnapshot.from_entity(entity)

    # Assert
    assert snapshot.zone_id == zone_id
    assert snapshot.density == 0.8
    assert snapshot.queue_waiting_minutes == 20
    assert snapshot.last_updated == entity.last_updated

@pytest.mark.asyncio
async def test_service_get_state_found() -> None:
    # Arrange
    repo = MagicMock(spec=OperationalStateRepository)
    publisher = MagicMock(spec=EventPublisher)
    service = OperationalStateService(repo, publisher)
    
    zone_id = uuid4()
    entity = OperationalStateFactory.create(zone_id, density=0.3, queue_waiting_minutes=6)
    repo.get_by_id = AsyncMock(return_value=entity)

    # Act
    snapshot = await service.get_state(zone_id)

    # Assert
    assert snapshot is not None
    assert snapshot.density == 0.3
    repo.get_by_id.assert_called_once_with(zone_id)

@pytest.mark.asyncio
async def test_service_get_state_not_found() -> None:
    # Arrange
    repo = MagicMock(spec=OperationalStateRepository)
    publisher = MagicMock(spec=EventPublisher)
    service = OperationalStateService(repo, publisher)

    zone_id = uuid4()
    repo.get_by_id = AsyncMock(return_value=None)

    # Act
    snapshot = await service.get_state(zone_id)

    # Assert
    assert snapshot is None

@pytest.mark.asyncio
async def test_service_update_state_new_zone() -> None:
    # Arrange
    repo = MagicMock(spec=OperationalStateRepository)
    publisher = MagicMock(spec=EventPublisher)
    service = OperationalStateService(repo, publisher)

    zone_id = uuid4()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    coords = Coordinates(latitude=10.0, longitude=20.0)

    # Act
    snapshot = await service.update_state(
        zone_id=zone_id,
        density=0.6,
        queue_waiting_minutes=8,
        coordinates=coords,
    )

    # Assert
    assert snapshot.density == 0.6
    assert snapshot.queue_waiting_minutes == 8
    repo.save.assert_called_once()
    publisher.publish_many.assert_not_called()

@pytest.mark.asyncio
async def test_service_update_state_existing_zone() -> None:
    # Arrange
    repo = MagicMock(spec=OperationalStateRepository)
    publisher = MagicMock(spec=EventPublisher)
    service = OperationalStateService(repo, publisher)

    zone_id = uuid4()
    entity = OperationalStateFactory.create(zone_id, density=0.1, queue_waiting_minutes=2)
    repo.get_by_id = AsyncMock(return_value=entity)
    repo.save = AsyncMock()
    publisher.publish_many = AsyncMock()
    coords = Coordinates(latitude=10.0, longitude=20.0)

    # Act
    snapshot = await service.update_state(
        zone_id=zone_id,
        density=0.9,
        queue_waiting_minutes=25,
        coordinates=coords,
    )

    # Assert
    assert snapshot.density == 0.9
    assert snapshot.queue_waiting_minutes == 25
    repo.save.assert_called_once()
    # It should have registered a CrowdDensityChanged event and cleared it after publishing
    publisher.publish_many.assert_called_once()
    assert len(entity.domain_events) == 0
