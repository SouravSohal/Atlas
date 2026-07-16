from collections.abc import Iterator
from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def override_dashboard_dependencies(client: TestClient) -> Iterator[tuple[MagicMock, MagicMock, MagicMock]]:
    app = cast(FastAPI, client.app)
    container = app.state.container

    mock_incident_repo = MagicMock()
    mock_state_repo = MagicMock()
    mock_rec_repo = MagicMock()

    # Dynamic mock implementation for incident list_paginated
    async def mock_incident_list_paginated(
        page=1, limit=10, resolved=None, severity=None, incident_type=None, sort_by="created_at", order="desc"
    ):
        items = []
        if isinstance(mock_incident_repo.list, AsyncMock):
            try:
                items = await mock_incident_repo.list()
            except Exception:
                pass
        
        if resolved is not None:
            items = [i for i in items if i.resolved == resolved]
        if severity is not None:
            items = [i for i in items if i.severity.value == severity]
        if incident_type is not None:
            items = [i for i in items if i.incident_type.value == incident_type]
            
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        if sort_by == "severity":
            items = sorted(items, key=lambda x: severity_order.get(x.severity.value, 0), reverse=(order == "desc"))
        else:
            items = sorted(items, key=lambda x: x.created_at, reverse=(order == "desc"))
            
        total = len(items)
        start = (page - 1) * limit
        paginated = items[start:start+limit]
        return paginated, total

    mock_incident_repo.list_paginated = AsyncMock(side_effect=mock_incident_list_paginated)

    # Dynamic mock implementation for recommendation list_paginated
    async def mock_rec_list_paginated(
        page=1, limit=10, status=None, priority=None, action_type=None, sort_by="created_at", order="desc"
    ):
        items = []
        if isinstance(mock_rec_repo.list, AsyncMock):
            try:
                items = await mock_rec_repo.list()
            except Exception:
                pass
        
        if status is not None:
            items = [r for r in items if r.status.value == status]
        if priority is not None:
            items = [r for r in items if r.priority.value == priority]
        if action_type is not None:
            items = [r for r in items if r.action_type == action_type]
            
        if sort_by == "confidence":
            items = sorted(items, key=lambda x: x.confidence.value, reverse=(order == "desc"))
        else:
            items = sorted(items, key=lambda x: x.created_at, reverse=(order == "desc"))
            
        total = len(items)
        start = (page - 1) * limit
        paginated = items[start:start+limit]
        return paginated, total

    mock_rec_repo.list_paginated = AsyncMock(side_effect=mock_rec_list_paginated)

    container.incident_repository.override(mock_incident_repo)
    container.operational_state_repository.override(mock_state_repo)
    container.recommendation_repository.override(mock_rec_repo)

    yield mock_incident_repo, mock_state_repo, mock_rec_repo

    container.reset_override()


def test_dashboard_overview_success(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_incident_repo, mock_state_repo, mock_rec_repo = override_dashboard_dependencies

    # Setup mock data for state managers / snapshots
    mock_state = OperationalState(
        zone_id=uuid4(),
        density=CrowdDensity(value=0.55),
        queue_estimate=QueueEstimate(waiting_minutes=15),
        last_updated=datetime.now(UTC),
    )
    mock_incident = Incident(
        id=uuid4(),
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Active incident",
        location=Coordinates(latitude=10.0, longitude=20.0),
        reporter_id=uuid4(),
        resolved=False,
    )
    mock_rec = Recommendation(
        action_type="OPEN_GATES",
        priority=Severity.HIGH,
        confidence=ConfidenceScore(value=0.95),
        details="Open gates details",
        status=RecommendationStatus.PENDING,
    )

    mock_state_repo.list = AsyncMock(return_value=[mock_state])
    mock_incident_repo.list = AsyncMock(return_value=[mock_incident])
    mock_rec_repo.list = AsyncMock(return_value=[mock_rec])
    # Empty task list for volunteer metrics
    app = cast(FastAPI, client.app)
    app.state.container.task_repository.override(MagicMock())
    app.state.container.task_repository().list = AsyncMock(return_value=[])

    # Act
    with client:
        response = client.get("/dashboard/overview")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["stadium_health"] < 1.0  # High severity incident decreases health
    assert data["data"]["active_incidents_count"] == 1
    assert data["data"]["average_crowd_density"] == pytest.approx(0.55)


def test_dashboard_incidents_filtering_and_sorting(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_incident_repo, _, _ = override_dashboard_dependencies

    inc_low = Incident(
        incident_type=IncidentType.MEDICAL,
        severity=Severity.LOW,
        description="Stub minor",
        location=Coordinates(latitude=10.0, longitude=20.0),
        reporter_id=uuid4(),
        resolved=True,
    )
    inc_high = Incident(
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Stub major",
        location=Coordinates(latitude=10.1, longitude=20.1),
        reporter_id=uuid4(),
        resolved=False,
    )

    mock_incident_repo.list = AsyncMock(return_value=[inc_low, inc_high])

    # Act: Request active (unresolved) incidents sorted by severity desc
    with client:
        response = client.get("/dashboard/incidents?resolved=false&sort_by=severity&order=desc")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    items = data["data"]["items"]
    assert len(items) == 1
    assert items[0]["description"] == "Stub major"
    assert items[0]["severity"] == "high"


def test_dashboard_operational_state(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    _, mock_state_repo, _ = override_dashboard_dependencies

    mock_state = OperationalState(
        zone_id=uuid4(),
        density=CrowdDensity(value=0.4),
        queue_estimate=QueueEstimate(waiting_minutes=8),
        last_updated=datetime.now(UTC),
    )
    mock_state_repo.list = AsyncMock(return_value=[mock_state])

    # Act
    with client:
        response = client.get("/dashboard/operational-state")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["density"] == pytest.approx(0.4)
    assert data["data"][0]["queue_waiting_minutes"] == 8


def test_dashboard_recommendations(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    _, _, mock_rec_repo = override_dashboard_dependencies

    rec_a = Recommendation(
        action_type="REROUTE_CROWD",
        priority=Severity.MEDIUM,
        confidence=ConfidenceScore(value=0.8),
        details="Details A",
        status=RecommendationStatus.PENDING,
    )
    rec_b = Recommendation(
        action_type="OPEN_GATES",
        priority=Severity.HIGH,
        confidence=ConfidenceScore(value=0.95),
        details="Details B",
        status=RecommendationStatus.APPROVED,
        approved_by_id=uuid4(),
        approved_at=datetime.now(UTC),
    )
    mock_rec_repo.list = AsyncMock(return_value=[rec_a, rec_b])

    # Act: filter status approved
    with client:
        response = client.get("/dashboard/recommendations?status=approved")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    items = data["data"]["items"]
    assert len(items) == 1
    assert items[0]["action_type"] == "OPEN_GATES"
    assert items[0]["status"] == "approved"


def test_dashboard_metrics(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_incident_repo, mock_state_repo, mock_rec_repo = override_dashboard_dependencies

    # Setup states (one congested, one not)
    mock_state1 = OperationalState(
        zone_id=uuid4(),
        density=CrowdDensity(value=0.85),
        queue_estimate=QueueEstimate(waiting_minutes=25),
        last_updated=datetime.now(UTC),
    )
    mock_state2 = OperationalState(
        zone_id=uuid4(),
        density=CrowdDensity(value=0.3),
        queue_estimate=QueueEstimate(waiting_minutes=5),
        last_updated=datetime.now(UTC),
    )
    mock_state_repo.list = AsyncMock(return_value=[mock_state1, mock_state2])

    # Setup incidents
    inc_1 = Incident(
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Sec",
        location=Coordinates(latitude=0, longitude=0),
        reporter_id=uuid4(),
        resolved=False,
    )
    inc_2 = Incident(
        incident_type=IncidentType.MEDICAL,
        severity=Severity.LOW,
        description="Med",
        location=Coordinates(latitude=0, longitude=0),
        reporter_id=uuid4(),
        resolved=True,
    )
    mock_incident_repo.list = AsyncMock(return_value=[inc_1, inc_2])

    # Setup recommendations
    rec = Recommendation(
        action_type="OPEN_GATES",
        priority=Severity.HIGH,
        confidence=ConfidenceScore(value=0.9),
        details="Details",
        status=RecommendationStatus.PENDING,
    )
    mock_rec_repo.list = AsyncMock(return_value=[rec])

    # Act
    with client:
        response = client.get("/dashboard/metrics")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    metrics = data["data"]
    # Average queue: (25 + 5) / 2 = 15.0
    assert metrics["average_queue_wait_minutes"] == pytest.approx(15.0)
    # Congestion rate: 1 zone out of 2 is > 0.75 => 0.5
    assert metrics["congestion_rate"] == pytest.approx(0.5)
    # Incident resolution rate: 1 out of 2 is resolved => 0.5
    assert metrics["incident_resolution_rate"] == pytest.approx(0.5)
    assert metrics["incidents_by_severity"]["high"] == 1
    assert metrics["incidents_by_type"]["security"] == 1
    assert metrics["recommendations_by_status"]["pending"] == 1


def test_dashboard_incidents_extra_filters(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    mock_incident_repo, _, _ = override_dashboard_dependencies

    inc = Incident(
        incident_type=IncidentType.SECURITY,
        severity=Severity.HIGH,
        description="Major Security",
        location=Coordinates(latitude=10.0, longitude=20.0),
        reporter_id=uuid4(),
        resolved=False,
    )
    mock_incident_repo.list = AsyncMock(return_value=[inc])

    with client:
        response = client.get("/dashboard/incidents?severity=high&incident_type=security&sort_by=created_at&order=asc")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["items"]) == 1


def test_dashboard_recommendations_extra_filters(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    _, _, mock_rec_repo = override_dashboard_dependencies

    rec = Recommendation(
        action_type="OPEN_GATES",
        priority=Severity.HIGH,
        confidence=ConfidenceScore(value=0.95),
        details="Details",
        status=RecommendationStatus.PENDING,
    )
    mock_rec_repo.list = AsyncMock(return_value=[rec])

    with client:
        response = client.get("/dashboard/recommendations?priority=high&action_type=OPEN_GATES&sort_by=confidence&order=asc")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["items"]) == 1


def test_dashboard_predictions_success(
    client: TestClient,
    override_dashboard_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    # Arrange
    mock_incident_repo, mock_state_repo, mock_rec_repo = override_dashboard_dependencies
    mock_state_repo.list = AsyncMock(return_value=[])
    mock_incident_repo.list = AsyncMock(return_value=[])
    mock_rec_repo.list = AsyncMock(return_value=[])

    app = cast(FastAPI, client.app)
    container = app.state.container

    mock_task_repo = MagicMock()
    mock_task_repo.list = AsyncMock(return_value=[])
    container.task_repository.override(mock_task_repo)

    mock_event_repo = MagicMock()
    mock_event_repo.list = AsyncMock(return_value=[])
    container.event_repository.override(mock_event_repo)

    mock_predictions_agent = MagicMock()
    from app.application.operational_state.predictions_agent import StadiumPredictionsResponse, PredictionItem
    mock_response = StadiumPredictionsResponse(
        confidence_score=0.9,
        rationale="R",
        queue_growth=PredictionItem(prediction="Q", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        crowd_movement=PredictionItem(prediction="C", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        volunteer_shortages=PredictionItem(prediction="V", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        medical_demand=PredictionItem(prediction="Me", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        transport_congestion=PredictionItem(prediction="Tr", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        gate_overload=PredictionItem(prediction="G", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        parking_saturation=PredictionItem(prediction="P", confidence=0.8, reason="R", mitigation="M", timeline="T"),
        weather_impact=PredictionItem(prediction="W", confidence=0.8, reason="R", mitigation="M", timeline="T"),
    )
    mock_predictions_agent.generate_predictions = AsyncMock(return_value=mock_response)
    container.stadium_predictions_agent.override(mock_predictions_agent)

    # Act
    with client:
        response = client.get("/dashboard/predictions")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["queue_growth"]["prediction"] == "Q"

    # Cleanup
    container.reset_override()

