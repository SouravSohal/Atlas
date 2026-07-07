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


def test_updater_apply_incident_created() -> None:
    # Arrange
    from atlas_core.domain.enums.incident_type import IncidentType
    from atlas_core.domain.enums.severity import Severity
    from atlas_core.domain.events.incident_created import IncidentCreated
    
    zone_id = uuid4()
    state = OperationalStateFactory.create(zone_id, density=0.5, queue_waiting_minutes=10)
    coords = Coordinates(latitude=10.0, longitude=20.0)
    
    event = IncidentCreated(
        aggregate_id=zone_id,
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Gate breach",
        location=coords,
        reporter_id=uuid4(),
    )

    # Act
    OperationalStateUpdater.apply_incident_created(state, event, coords)

    # Assert
    assert state.density.value == 0.7
    assert state.queue_estimate.waiting_minutes == 15


def test_updater_apply_crowd_density_changed() -> None:
    # Arrange
    from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
    from atlas_core.domain.value_objects.crowd_density import CrowdDensity
    
    zone_id = uuid4()
    state = OperationalStateFactory.create(zone_id, density=0.2, queue_waiting_minutes=5)
    coords = Coordinates(latitude=10.0, longitude=20.0)
    
    event = CrowdDensityChanged(
        aggregate_id=zone_id,
        location=coords,
        previous_density=CrowdDensity(value=0.2),
        new_density=CrowdDensity(value=0.9),
    )

    # Act
    OperationalStateUpdater.apply_crowd_density_changed(state, event, coords)

    # Assert
    assert state.density.value == 0.9


def test_updater_apply_recommendation_approved() -> None:
    # Arrange
    from atlas_core.domain.events.recommendation_approved import RecommendationApproved
    
    zone_id = uuid4()
    state = OperationalStateFactory.create(zone_id, density=0.8, queue_waiting_minutes=20)
    coords = Coordinates(latitude=10.0, longitude=20.0)
    
    event = RecommendationApproved(
        aggregate_id=zone_id,
        approved_by=uuid4(),
    )

    # Act
    OperationalStateUpdater.apply_recommendation_approved(state, event, coords)

    # Assert
    assert state.density.value == pytest.approx(0.7)
    assert state.queue_estimate.waiting_minutes == 15


def test_updater_apply_recommendation_generated() -> None:
    # Arrange
    from atlas_core.domain.enums.severity import Severity
    from atlas_core.domain.events.recommendation_generated import RecommendationGenerated
    from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
    
    zone_id = uuid4()
    state = OperationalStateFactory.create(zone_id, density=0.4, queue_waiting_minutes=12)
    coords = Coordinates(latitude=10.0, longitude=20.0)
    
    event = RecommendationGenerated(
        aggregate_id=zone_id,
        action_type="reroute",
        priority=Severity.HIGH,
        confidence=ConfidenceScore(value=0.85),
        details="Reroute crowd",
    )

    # Act
    OperationalStateUpdater.apply_recommendation_generated(state, event, coords)

    # Assert
    assert state.density.value == 0.4
    assert state.queue_estimate.waiting_minutes == 12


def test_updater_apply_gate_status_changed() -> None:
    # Arrange
    from app.application.operational_state import GateStatusChanged
    
    zone_id = uuid4()
    state = OperationalStateFactory.create(zone_id, density=0.5, queue_waiting_minutes=10)
    coords = Coordinates(latitude=10.0, longitude=20.0)
    
    event = GateStatusChanged(
        aggregate_id=zone_id,
        gate_id=uuid4(),
        status="closed",
    )

    # Act
    OperationalStateUpdater.apply_gate_status_changed(state, event, coords)

    # Assert
    assert state.density.value == pytest.approx(0.65)
    assert state.queue_estimate.waiting_minutes == 20


def test_updater_apply_volunteer_assigned() -> None:
    # Arrange
    from app.application.operational_state import VolunteerAssigned
    
    zone_id = uuid4()
    state = OperationalStateFactory.create(zone_id, density=0.5, queue_waiting_minutes=10)
    coords = Coordinates(latitude=10.0, longitude=20.0)
    
    event = VolunteerAssigned(
        aggregate_id=zone_id,
        task_id=uuid4(),
        volunteer_id=uuid4(),
    )

    # Act
    OperationalStateUpdater.apply_volunteer_assigned(state, event, coords)

    # Assert
    assert state.density.value == pytest.approx(0.45)


@pytest.mark.asyncio
async def test_state_manager_get_snapshot() -> None:
    # Arrange
    from atlas_core.domain.repositories.incident_repository import IncidentRepository
    from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
    from atlas_core.domain.repositories.task_repository import TaskRepository

    from app.application.operational_state import OperationalStateManager
    
    state_repo = MagicMock(spec=OperationalStateRepository)
    incident_repo = MagicMock(spec=IncidentRepository)
    task_repo = MagicMock(spec=TaskRepository)
    rec_repo = MagicMock(spec=RecommendationRepository)
    publisher = MagicMock(spec=EventPublisher)

    # mock incidents
    mock_inc1 = MagicMock()
    mock_inc1.resolved = False
    mock_inc1.severity.value = "high"
    mock_inc1.id = uuid4()
    
    mock_inc2 = MagicMock()
    mock_inc2.resolved = True
    
    incident_repo.list = AsyncMock(return_value=[mock_inc1, mock_inc2])

    # mock states
    zone1 = uuid4()
    zone2 = uuid4()
    state1 = OperationalStateFactory.create(zone1, density=0.9, queue_waiting_minutes=25)
    state2 = OperationalStateFactory.create(zone2, density=0.3, queue_waiting_minutes=5)
    state_repo.list = AsyncMock(return_value=[state1, state2])

    # mock recs
    mock_rec = MagicMock()
    mock_rec.status.value = "pending"
    mock_rec.id = uuid4()
    rec_repo.list = AsyncMock(return_value=[mock_rec])

    # mock tasks
    mock_task = MagicMock()
    mock_task.assigned_to_id = uuid4()
    mock_task.id = uuid4()
    task_repo.list = AsyncMock(return_value=[mock_task])

    manager = OperationalStateManager(state_repo, incident_repo, task_repo, rec_repo, publisher)

    # Act
    snapshot = await manager.get_snapshot()

    # Assert
    assert snapshot.stadium_health < 1.0
    assert snapshot.crowd_conditions[zone1] == 0.9
    assert snapshot.queue_information[zone2] == 5
    assert len(snapshot.active_incidents) == 1
    assert len(snapshot.recommendations) == 1
    assert snapshot.volunteer_allocation[mock_task.id] == mock_task.assigned_to_id


@pytest.mark.asyncio
async def test_state_manager_update_zone_state() -> None:
    # Arrange
    from atlas_core.domain.repositories.incident_repository import IncidentRepository
    from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
    from atlas_core.domain.repositories.task_repository import TaskRepository

    from app.application.operational_state import (
        InvalidStateTransitionException,
        OperationalStateManager,
    )

    state_repo = MagicMock(spec=OperationalStateRepository)
    incident_repo = MagicMock(spec=IncidentRepository)
    task_repo = MagicMock(spec=TaskRepository)
    rec_repo = MagicMock(spec=RecommendationRepository)
    publisher = MagicMock(spec=EventPublisher)

    incident_repo.list = AsyncMock(return_value=[])
    state_repo.list = AsyncMock(return_value=[])
    rec_repo.list = AsyncMock(return_value=[])
    task_repo.list = AsyncMock(return_value=[])
    publisher.publish_many = AsyncMock()

    zone_id = uuid4()
    state_repo.get_by_id = AsyncMock(return_value=None)
    state_repo.save = AsyncMock()

    manager = OperationalStateManager(state_repo, incident_repo, task_repo, rec_repo, publisher)
    coords = Coordinates(latitude=10.0, longitude=20.0)

    # Act: Update new state
    await manager.update_zone_state(zone_id, 0.5, 10, coords)

    # Assert
    state_repo.save.assert_called_once()

    # Act & Assert: Invalid parameters
    with pytest.raises(InvalidStateTransitionException, match="Density value must be between"):
        await manager.update_zone_state(zone_id, 1.5, 10, coords)

    with pytest.raises(InvalidStateTransitionException, match="Queue waiting minutes cannot be negative"):
        await manager.update_zone_state(zone_id, 0.5, -5, coords)

