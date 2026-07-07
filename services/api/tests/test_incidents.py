from unittest.mock import AsyncMock, MagicMock
import pytest
from uuid import uuid4
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.coordinates import Coordinates
from app.application.operational_state import OperationalStateSnapshot
from app.presentation.responses import ApiResponse

@pytest.fixture
def override_dependencies(client: TestClient) -> tuple[MagicMock, MagicMock, MagicMock]:
    container = client.app.state.container

    mock_repo = MagicMock()
    mock_state_service = MagicMock()
    mock_publisher = MagicMock()

    container.incident_repository.override(mock_repo)
    container.operational_state_service.override(mock_state_service)
    container.event_publisher.override(mock_publisher)

    yield mock_repo, mock_state_service, mock_publisher

    container.unoverride()

def test_create_incident_success(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, mock_state_service, mock_publisher = override_dependencies
    
    # Mock Repository save
    mock_repo.save = AsyncMock()

    # Mock Operational State get_state returning None, and update_state returning snapshot
    mock_state_service.get_state = AsyncMock(return_value=None)
    mock_snapshot = OperationalStateSnapshot(
        zone_id=uuid4(),
        density=0.0,
        queue_waiting_minutes=0,
        last_updated=datetime.now(UTC),
    )
    mock_state_service.update_state = AsyncMock(return_value=mock_snapshot)

    # Mock event publisher
    mock_publisher.publish_many = AsyncMock()

    reporter_id = uuid4()
    zone_id = uuid4()
    payload = {
        "incident_type": "security",
        "severity": "high",
        "description": "Gate breach detected",
        "latitude": 34.05,
        "longitude": -118.25,
        "reporter_id": str(reporter_id),
        "zone_id": str(zone_id),
    }

    # Act
    with client:
        response = client.post("/incidents", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["incident_type"] == "security"
    assert data["data"]["severity"] == "high"
    assert data["data"]["description"] == "Gate breach detected"

    mock_repo.save.assert_called_once()
    mock_state_service.get_state.assert_called_once_with(zone_id)
    mock_state_service.update_state.assert_called_once()
    mock_publisher.publish_many.assert_called_once()

def test_get_incident_success(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, _, _ = override_dependencies
    incident_id = uuid4()
    reporter_id = uuid4()

    mock_incident = Incident(
        id=incident_id,
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Gate breach detected",
        location=Coordinates(latitude=34.05, longitude=-118.25),
        reporter_id=reporter_id,
    )
    mock_repo.get_by_id = AsyncMock(return_value=mock_incident)

    # Act
    with client:
        response = client.get(f"/incidents/{incident_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(incident_id)
    assert data["data"]["description"] == "Gate breach detected"
    mock_repo.get_by_id.assert_called_once_with(incident_id)

def test_get_incident_not_found(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, _, _ = override_dependencies
    incident_id = uuid4()
    mock_repo.get_by_id = AsyncMock(return_value=None)

    # Act
    with client:
        response = client.get(f"/incidents/{incident_id}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["error"].lower()

def test_list_incidents(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, _, _ = override_dependencies
    reporter_id = uuid4()

    mock_incidents = [
        Incident(
            incident_type=IncidentType.SECURITY,
            severity=Severity.HIGH,
            description="Intrusion A",
            location=Coordinates(latitude=34.0, longitude=-118.0),
            reporter_id=reporter_id,
        ),
        Incident(
            incident_type=IncidentType.MEDICAL,
            severity=Severity.LOW,
            description="Injury B",
            location=Coordinates(latitude=34.1, longitude=-118.1),
            reporter_id=reporter_id,
        ),
    ]
    mock_repo.list = AsyncMock(return_value=mock_incidents)

    # Act
    with client:
        response = client.get("/incidents")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["description"] == "Intrusion A"
    assert data["data"][1]["description"] == "Injury B"
    mock_repo.list.assert_called_once()
