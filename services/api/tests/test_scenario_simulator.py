from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.operational_state.snapshot import OperationalSnapshot
from app.application.operational_state.state_manager import OperationalStateManager
from app.application.recommendations.engine import RecommendationEngine
from app.application.scenario_simulator import (
    ImpactAnalyzer,
    Scenario,
    ScenarioBuilder,
    ScenarioExecutor,
    ScenarioSimulator,
    ScenarioValidator,
    SimulationHistory,
    SimulationRecord,
    SimulationReport,
    SimulationService,
)
from app.intelligence import AIOrchestrator, PromptRegistry


@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

@pytest.fixture
def mock_state_manager() -> MagicMock:
    state_manager = MagicMock(spec=OperationalStateManager)
    # Return a mock OperationalSnapshot
    mock_snapshot = OperationalSnapshot(
        active_incidents=[],
        crowd_conditions={uuid4(): 0.2, uuid4(): 0.3},
        recommendations=[],
        volunteer_allocation={},
        queue_information={uuid4(): 5, uuid4(): 10},
        stadium_health=1.0,
        timestamp=datetime.now(UTC),
    )
    state_manager.get_snapshot = AsyncMock(return_value=mock_snapshot)
    return state_manager

@pytest.fixture
def mock_recommendation_engine() -> MagicMock:
    engine = MagicMock(spec=RecommendationEngine)
    engine.generate = MagicMock(return_value=[])
    return engine

def test_scenario_builder() -> None:
    # Success construction
    zone_id = uuid4()
    scenario = (
        ScenarioBuilder()
        .with_type("Gate Closure")
        .with_zone(zone_id)
        .with_severity("high")
        .with_description("Hypothetical closure of Gate 1.")
        .with_param("custom_key", "custom_val")
        .build()
    )

    assert scenario.scenario_type == "Gate Closure"
    assert scenario.zone_id == zone_id
    assert scenario.severity == "high"
    assert scenario.description == "Hypothetical closure of Gate 1."
    assert scenario.params["custom_key"] == "custom_val"

    # Validation errors on builder
    with pytest.raises(ValueError, match="Scenario type is required"):
        ScenarioBuilder().with_description("Missing type").build()

    with pytest.raises(ValueError, match="Scenario description is required"):
        ScenarioBuilder().with_type("Gate Closure").build()

def test_scenario_validator() -> None:
    validator = ScenarioValidator()

    # Valid scenario
    valid_scenario = Scenario(
        scenario_type="Gate Closure",
        description="Gate 1 Closure",
        severity="high",
    )
    validator.validate(valid_scenario)  # Should not raise

    # Invalid type
    invalid_type = Scenario(
        scenario_type="Alien Invasion",
        description="Not supported scenario",
    )
    with pytest.raises(ValueError, match="Unsupported scenario type"):
        validator.validate(invalid_type)

    # Invalid severity
    invalid_severity = Scenario(
        scenario_type="Gate Closure",
        description="Supported type",
        severity="extreme",
    )
    with pytest.raises(ValueError, match="Invalid severity level"):
        validator.validate(invalid_severity)

    # Empty description
    invalid_desc = Scenario(
        scenario_type="Gate Closure",
        description="  ",
    )
    with pytest.raises(ValueError, match="description cannot be empty"):
        validator.validate(invalid_desc)

def test_scenario_executor() -> None:
    executor = ScenarioExecutor()
    zone_1 = uuid4()
    zone_2 = uuid4()
    initial_snapshot = OperationalSnapshot(
        active_incidents=[],
        crowd_conditions={zone_1: 0.2, zone_2: 0.3},
        recommendations=[],
        volunteer_allocation={},
        queue_information={zone_1: 5, zone_2: 10},
        stadium_health=1.0,
        timestamp=datetime.now(UTC),
    )

    # Test Gate Closure
    scenario_closure = Scenario(
        scenario_type="Gate Closure",
        zone_id=zone_1,
        description="Close gate 1",
    )
    updated, effects = executor.execute(initial_snapshot, scenario_closure)
    assert updated.crowd_conditions[zone_1] == 0.0
    assert updated.queue_information[zone_1] == 0
    assert updated.crowd_conditions[zone_2] > 0.3  # Rerouted surge

    # Test Crowd Surge
    scenario_surge = Scenario(
        scenario_type="Crowd Surge",
        zone_id=zone_2,
        description="Surge in zone 2",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_surge)
    assert updated.crowd_conditions[zone_2] == pytest.approx(0.65)  # 0.3 + 0.35

    # Test Crowd Surge global (no zone specified)
    scenario_surge_global = Scenario(
        scenario_type="Crowd Surge",
        description="Global surge",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_surge_global)
    assert updated.crowd_conditions[zone_1] == pytest.approx(0.4)  # 0.2 + 0.20

    # Test Medical Emergency
    scenario_medical = Scenario(
        scenario_type="Medical Emergency",
        zone_id=zone_1,
        description="Medical crisis",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_medical)
    assert len(updated.active_incidents) == 1
    assert updated.queue_information[zone_1] == 9

    # Test Heavy Rain
    scenario_rain = Scenario(
        scenario_type="Heavy Rain",
        description="Severe storm",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_rain)
    assert updated.queue_information[zone_1] == 15

    # Test Public Transport Delay
    scenario_transport = Scenario(
        scenario_type="Public Transport Delay",
        description="Train delayed",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_transport)
    assert updated.crowd_conditions[zone_1] == pytest.approx(0.35)

    # Test Power Failure
    scenario_power = Scenario(
        scenario_type="Power Failure",
        description="Power failure",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_power)
    assert updated.queue_information[zone_1] == 30

    # Test VIP Arrival
    scenario_vip = Scenario(
        scenario_type="VIP Arrival",
        zone_id=zone_2,
        description="Corridor secure",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_vip)
    assert updated.queue_information[zone_2] == 18

    # Test Security Incident
    scenario_security = Scenario(
        scenario_type="Security Incident",
        description="Security breach",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_security)
    assert len(updated.active_incidents) == 1

    # Test Lost Child
    scenario_child = Scenario(
        scenario_type="Lost Child",
        zone_id=zone_1,
        description="Lost child near zone 1",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_child)
    assert updated.queue_information[zone_1] == 10

    # Test Evacuation
    scenario_evac = Scenario(
        scenario_type="Evacuation",
        description="Stadium Evacuation",
    )
    updated, _ = executor.execute(initial_snapshot, scenario_evac)
    assert updated.crowd_conditions[zone_1] == 0.95
    assert updated.queue_information[zone_1] == 99

@pytest.mark.asyncio
async def test_impact_analyzer(mock_orchestrator: MagicMock) -> None:
    expected_report = SimulationReport(
        confidence_score=0.98,
        rationale="Completed simulation.",
        operational_impact="Elevated risk near Gate 1",
        estimated_queue_changes="Queues increasing (+10 mins)",
        resource_utilization="Allocate 4 extra volunteers",
        risk_score=0.75,
        recommended_actions=["Open gate 2", "Deploy volunteers"],
        predicted_bottlenecks=["Gate 1 Entry"],
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_report)

    analyzer = ImpactAnalyzer(mock_orchestrator)
    registered_prompt = mock_orchestrator.registry.get("scenario_simulator_agent", "latest")
    assert "You are the ATLAS Stadium Operations Scenario Simulator AI Agent." in registered_prompt.template

    scenario = Scenario(
        scenario_type="Gate Closure",
        description="Close gate 1",
    )
    mock_cloned_state = OperationalSnapshot(
        active_incidents=[],
        crowd_conditions={},
        recommendations=[],
        volunteer_allocation={},
        queue_information={},
        stadium_health=1.0,
        timestamp=datetime.now(UTC),
    )

    report = await analyzer.analyze(scenario, mock_cloned_state, {"action": "simulated"})
    assert report.risk_score == 0.75
    assert "Gate 1 Entry" in report.predicted_bottlenecks
    mock_orchestrator.execute.assert_called_once()

def test_simulation_history() -> None:
    history = SimulationHistory()
    assert len(history.list()) == 0

    scenario = Scenario(
        scenario_type="Gate Closure",
        description="Close gate 1",
    )
    report = SimulationReport(
        confidence_score=0.98,
        rationale="Done",
        operational_impact="Impact",
        estimated_queue_changes="No change",
        resource_utilization="None",
        risk_score=0.1,
        recommended_actions=[],
        predicted_bottlenecks=[],
    )
    record = SimulationRecord(
        scenario=scenario,
        timestamp=datetime.now(UTC),
        report=report,
        direct_effects={},
    )

    history.add(record)
    assert len(history.list()) == 1
    assert history.get(record.id) == record

    history.clear()
    assert len(history.list()) == 0

@pytest.mark.asyncio
async def test_simulation_service(
    mock_state_manager: MagicMock,
    mock_orchestrator: MagicMock,
    mock_recommendation_engine: MagicMock,
) -> None:
    expected_report = SimulationReport(
        confidence_score=0.95,
        rationale="Passed",
        operational_impact="Test Impact",
        estimated_queue_changes="Wait queue +5 mins",
        resource_utilization="Deploy extra units",
        risk_score=0.4,
        recommended_actions=["Deploy Security"],
        predicted_bottlenecks=["Gate 1"],
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_report)
    analyzer = ImpactAnalyzer(mock_orchestrator)
    history = SimulationHistory()

    service = SimulationService(
        state_manager=mock_state_manager,
        impact_analyzer=analyzer,
        rec_engine=mock_recommendation_engine,
        history=history,
    )

    scenario = Scenario(
        scenario_type="Gate Closure",
        description="Close gate 1",
    )

    record = await service.run_simulation(scenario)
    assert record.report.risk_score == 0.4
    assert len(history.list()) == 1
    mock_state_manager.get_snapshot.assert_called_once()
    mock_recommendation_engine.generate.assert_called_once()

@pytest.mark.asyncio
async def test_scenario_simulator_facade(
    mock_state_manager: MagicMock,
    mock_orchestrator: MagicMock,
    mock_recommendation_engine: MagicMock,
) -> None:
    expected_report = SimulationReport(
        confidence_score=0.95,
        rationale="Passed",
        operational_impact="Test Impact",
        estimated_queue_changes="Wait queue +5 mins",
        resource_utilization="Deploy extra units",
        risk_score=0.4,
        recommended_actions=["Deploy Security"],
        predicted_bottlenecks=["Gate 1"],
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_report)
    analyzer = ImpactAnalyzer(mock_orchestrator)
    history = SimulationHistory()

    service = SimulationService(
        state_manager=mock_state_manager,
        impact_analyzer=analyzer,
        rec_engine=mock_recommendation_engine,
        history=history,
    )
    simulator = ScenarioSimulator(service)

    record = await simulator.run(
        scenario_type="Gate Closure",
        description="Facade simulation of gate closure.",
    )
    assert record.scenario.scenario_type == "Gate Closure"
    assert record.report.confidence_score == 0.95
