import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from app.application.events import EventPublisher
from app.application.incidents.use_cases import CreateIncidentUseCase

from app.application.demo import (
    ScenarioDefinition,
    ScenarioStep,
    ScenarioState,
    ScenarioRegistry,
    ScenarioFactory,
    ScenarioRunner,
    ScenarioScheduler,
    DemoScenarioEngine,
)

@pytest.fixture
def mock_repos() -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    state_repo = MagicMock(spec=OperationalStateRepository)
    state_repo.save = AsyncMock()

    rec_repo = MagicMock(spec=RecommendationRepository)
    rec_repo.save = AsyncMock()

    create_incident_use_case = MagicMock(spec=CreateIncidentUseCase)
    create_incident_use_case.execute = AsyncMock()

    event_publisher = MagicMock(spec=EventPublisher)
    event_publisher.publish = AsyncMock()

    return state_repo, rec_repo, create_incident_use_case, event_publisher

def test_registry() -> None:
    registry = ScenarioRegistry()
    scen = ScenarioDefinition(name="Test", description="Desc")
    registry.register(scen)
    assert registry.get("Test") == scen
    assert "Test" in registry.list_all()

    with pytest.raises(KeyError):
        registry.get("Invalid")

def test_factory() -> None:
    zone_id = str(uuid4())
    cs = ScenarioFactory.create_crowd_surge(zone_id)
    assert cs.name == "Crowd Surge"
    assert len(cs.steps) == 3

    med = ScenarioFactory.create_medical_emergency(zone_id)
    assert med.name == "Medical Emergency"

    rain = ScenarioFactory.create_heavy_rain(zone_id)
    assert rain.name == "Heavy Rain"

    lost = ScenarioFactory.create_lost_child(zone_id)
    assert lost.name == "Lost Child"

    end = ScenarioFactory.create_match_end(zone_id)
    assert end.name == "Match End"

@pytest.mark.asyncio
async def test_runner(mock_repos) -> None:
    state_repo, rec_repo, create_incident_use_case, event_publisher = mock_repos
    runner = ScenarioRunner(state_repo, rec_repo, create_incident_use_case, event_publisher)

    zone_id = str(uuid4())
    step = ScenarioStep(
        tick_index=1,
        operational_state_updates={zone_id: 0.8},
        incidents_to_create=[{
            "incident_type": "crowd_control",
            "severity": "high",
            "description": "Crowd surge gate A",
            "zone_id": zone_id,
        }],
        notifications_to_publish=["Notif 1"],
        events_to_publish=[{"type": "TestEvent"}]
    )

    await runner.run_step(step)

    state_repo.save.assert_called_once()
    create_incident_use_case.execute.assert_called_once()
    event_publisher.publish.assert_called()
    rec_repo.save.assert_called()

@pytest.mark.asyncio
async def test_scheduler_and_engine(mock_repos) -> None:
    state_repo, rec_repo, create_incident_use_case, event_publisher = mock_repos
    engine = DemoScenarioEngine(state_repo, rec_repo, create_incident_use_case, event_publisher)

    # Validate registry has all standard scenarios
    assert len(engine.registry.list_all()) == 5

    # Trigger play
    await engine.set_speed(10.0) # speed up to 10x for testing
    status = engine.get_status()
    assert status["state"] == "stopped"

    # Play "Crowd Surge"
    await engine.play("Crowd Surge")
    status = engine.get_status()
    assert status["state"] == "playing"
    assert status["current_scenario"] == "Crowd Surge"

    # Pause
    await engine.pause()
    assert engine.scheduler.state == ScenarioState.PAUSED

    # Resume
    await engine.resume()
    assert engine.scheduler.state == ScenarioState.PLAYING

    # Wait for loop to finish or cancel
    await engine.reset()
    assert engine.scheduler.state == ScenarioState.STOPPED
    assert engine.scheduler.current_scenario is None
