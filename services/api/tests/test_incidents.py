from collections.abc import Iterator
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.coordinates import Coordinates
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.incidents.dtos import CreateIncidentRequest, UpdateIncidentRequest
from app.application.incidents.use_cases import CreateIncidentUseCase, UpdateIncidentUseCase


@pytest.fixture
def override_dependencies(client: TestClient) -> Iterator[tuple[MagicMock, MagicMock, MagicMock]]:
    app = cast(FastAPI, client.app)
    container = app.state.container

    mock_repo = MagicMock()
    mock_state_repo = MagicMock()
    mock_publisher = MagicMock()

    container.incident_repository.override(mock_repo)
    container.operational_state_repository.override(mock_state_repo)
    container.event_publisher.override(mock_publisher)

    yield mock_repo, mock_state_repo, mock_publisher

    container.reset_override()


def test_create_incident_success(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, mock_state_repo, mock_publisher = override_dependencies
    
    mock_repo.save = AsyncMock()
    mock_state_repo.get_by_id = AsyncMock(return_value=None)
    mock_state_repo.save = AsyncMock()
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
    mock_state_repo.get_by_id.assert_called_once_with(zone_id)
    mock_state_repo.save.assert_called_once()
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


def test_create_incident_value_error(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    _, _, _ = override_dependencies
    app = cast(FastAPI, client.app)
    container = app.state.container
    mock_use_case = MagicMock()
    mock_use_case.execute = AsyncMock(side_effect=ValueError("Invalid severity"))
    container.create_incident_use_case.override(mock_use_case)

    payload = {
        "incident_type": "security",
        "severity": "invalid",
        "description": "Breach",
        "latitude": 34.05,
        "longitude": -118.25,
        "reporter_id": str(uuid4()),
        "zone_id": str(uuid4()),
    }

    # Act
    with client:
        response = client.post("/incidents", json=payload)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "Invalid severity"


def test_update_incident_success(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, _, mock_publisher = override_dependencies
    incident_id = uuid4()
    reporter_id = uuid4()
    mock_incident = Incident(
        id=incident_id,
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Breach",
        location=Coordinates(latitude=10.0, longitude=20.0),
        reporter_id=reporter_id,
    )
    mock_repo.get_by_id = AsyncMock(return_value=mock_incident)
    mock_repo.save = AsyncMock()
    mock_publisher.publish_many = AsyncMock()

    payload = {
        "resolved": True,
        "severity": "low",
        "description": "Breach resolved",
    }

    # Act
    with client:
        response = client.patch(f"/incidents/{incident_id}", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["resolved"] is True
    assert data["data"]["severity"] == "low"
    assert data["data"]["description"] == "Breach resolved"
    mock_repo.save.assert_called_once()


def test_update_incident_not_found(
    client: TestClient,
    override_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_repo, _, _ = override_dependencies
    incident_id = uuid4()
    mock_repo.get_by_id = AsyncMock(return_value=None)

    payload = {"resolved": True}

    # Act
    with client:
        response = client.patch(f"/incidents/{incident_id}", json=payload)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["error"].lower()


@pytest.mark.asyncio
async def test_create_incident_use_case_logic() -> None:
    # Arrange
    mock_repo = MagicMock()
    mock_state_repo = MagicMock()
    mock_publisher = MagicMock()

    mock_repo.save = AsyncMock()
    mock_state_repo.get_by_id = AsyncMock(return_value=None)
    mock_state_repo.save = AsyncMock()
    mock_publisher.publish_many = AsyncMock()

    use_case = CreateIncidentUseCase(mock_repo, mock_state_repo, mock_publisher)

    reporter_id = uuid4()
    zone_id = uuid4()
    req = CreateIncidentRequest(
        incident_type="security",
        severity="high",
        description="Breach",
        latitude=34.05,
        longitude=-118.25,
        reporter_id=reporter_id,
        zone_id=zone_id,
    )

    # Act
    res = await use_case.execute(req)

    # Assert
    assert res.description == "Breach"
    assert res.severity == "high"
    mock_repo.save.assert_called_once()
    mock_state_repo.get_by_id.assert_called_once_with(zone_id)
    mock_state_repo.save.assert_called_once()
    mock_publisher.publish_many.assert_called_once()


@pytest.mark.asyncio
async def test_update_incident_use_case_logic() -> None:
    # Arrange
    mock_repo = MagicMock()
    mock_publisher = MagicMock()

    incident_id = uuid4()
    reporter_id = uuid4()
    mock_incident = Incident(
        id=incident_id,
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Breach",
        location=Coordinates(latitude=10.0, longitude=20.0),
        reporter_id=reporter_id,
    )

    mock_repo.get_by_id = AsyncMock(return_value=mock_incident)
    mock_repo.save = AsyncMock()
    mock_publisher.publish_many = AsyncMock()

    use_case = UpdateIncidentUseCase(mock_repo, mock_publisher)

    req = UpdateIncidentRequest(resolved=True, severity="low", description="Updated description")

    # Act
    res = await use_case.execute(incident_id, req)

    # Assert
    assert res is not None
    assert res.resolved is True
    assert res.severity == "low"
    assert res.description == "Updated description"
    mock_repo.get_by_id.assert_called_once_with(incident_id)
    mock_repo.save.assert_called_once()
