from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.intelligence import AIOrchestrator, PromptRegistry
from app.intelligence.predictive import (
    ArrivalPredictor,
    CongestionPredictor,
    ExitPredictor,
    PredictionResult,
    PredictiveIntelligenceEngine,
    QueuePredictor,
    RiskPredictor,
    VolunteerDemandPredictor,
)


# Simulated domain objects for testing
class MockOverview:
    def __init__(self, volunteers: int) -> None:
        self.allocated_volunteers_count = volunteers

class MockState:
    def __init__(self, zone_id: str, density: float, queue: int) -> None:
        self.zone_id = zone_id
        self.density = density
        self.queue_waiting_minutes = queue

class MockIncident:
    def __init__(self, severity: str, description: str, resolved: bool, zone_id: str) -> None:
        self.severity = severity
        self.description = description
        self.resolved = resolved
        self.zone_id = zone_id

@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

def test_congestion_predictor() -> None:
    predictor = CongestionPredictor()
    
    # Gate active, no incidents
    res_1 = predictor.predict(0.5, True, False)
    assert res_1 == 0.45

    # Gate inactive, incidents active
    res_2 = predictor.predict(0.5, False, True)
    assert res_2 == 0.75

def test_queue_predictor() -> None:
    predictor = QueuePredictor()
    
    # High density, low volunteers
    res_1 = predictor.predict(10, 0.85, 5)
    assert res_1 == 18

    # Low density, high volunteers
    res_2 = predictor.predict(10, 0.3, 20)
    assert res_2 == 6

def test_volunteer_demand_predictor() -> None:
    predictor = VolunteerDemandPredictor()
    
    # Critical density, multiple incidents
    res_1 = predictor.predict(0.85, 2)
    assert res_1 == 19

    # Nominal
    res_2 = predictor.predict(0.2, 0)
    assert res_2 == 5

def test_risk_predictor() -> None:
    predictor = RiskPredictor()
    
    # High risk
    res_1 = predictor.predict(0.9, 2)
    assert res_1 == 0.60

    # Low risk
    res_2 = predictor.predict(0.2, 0)
    assert res_2 == 0.05

def test_arrival_predictor() -> None:
    predictor = ArrivalPredictor()
    
    res_1 = predictor.predict_gate_utilization(0.4, 15)
    assert res_1 == 0.85

    res_2 = predictor.predict_gate_utilization(0.9, 45)
    assert res_2 == 0.65

def test_exit_predictor() -> None:
    predictor = ExitPredictor()
    
    res_1 = predictor.predict_egress_pressure("Match Completed", 0.3)
    assert res_1 == 0.90

    res_2 = predictor.predict_egress_pressure("First Half", 0.7)
    assert res_2 == 0.45

@pytest.mark.asyncio
async def test_predictive_engine(mock_orchestrator: MagicMock) -> None:
    expected_response = PredictionResult(
        confidence_score=0.97,
        rationale="Completed forecast.",
        predicted_crowd_density={},
        predicted_queue_length={},
        incident_probability={},
        volunteer_demand={},
        gate_utilization={},
        explanation="Operations expected to be stable.",
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_response)

    engine = PredictiveIntelligenceEngine(mock_orchestrator)
    
    # Assert registry
    registered_prompt = mock_orchestrator.registry.get("predictive_intelligence_agent", "latest")
    assert "You are the ATLAS Stadium Operations Predictive Intelligence AI Agent." in registered_prompt.template

    zone_id = str(uuid4())
    overview = MockOverview(15)
    states = [MockState(zone_id, 0.85, 20)]
    incidents = [MockIncident("critical", "Gate failure", False, zone_id)]
    recommendations = []

    # Act
    forecast = await engine.predict(overview, states, incidents, recommendations)

    # Assert
    assert forecast.explanation == "Operations expected to be stable."
    assert forecast.predicted_crowd_density[zone_id] == 0.95
    assert forecast.predicted_queue_length[zone_id] == 26
    assert forecast.incident_probability[zone_id] == 0.5
    assert forecast.volunteer_demand[zone_id] == 16
    mock_orchestrator.execute.assert_called_once()
