from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.intelligence import AIOrchestrator, PromptRegistry
from app.intelligence.decision_engine import (
    ConfidenceCalculator,
    DecisionContext,
    DecisionEngine,
    DecisionEngineResult,
    DecisionEvaluator,
    DecisionHistory,
    DecisionItem,
    DecisionPrioritizer,
    RiskScorer,
)


@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

def test_evaluator() -> None:
    evaluator = DecisionEvaluator()
    recs = [{"id": "rec-1", "details": "Redirection"}, {"id": None, "details": None}]
    filtered = evaluator.filter_valid_recommendations(recs)
    assert len(filtered) == 1
    assert filtered[0]["id"] == "rec-1"

def test_prioritizer() -> None:
    prioritizer = DecisionPrioritizer()
    item_low = DecisionItem(
        confidence_score=0.95,
        rationale="Done",
        original_recommendation_id="rec-1",
        priority="low",
        severity="low",
        confidence=0.9,
        expected_impact="Low impact",
        estimated_resolution_time="10m",
        required_resources=[],
        human_approval_requirement=False,
        suggested_operator_action="Inspect",
        explanation="None"
    )
    item_critical = DecisionItem(
        confidence_score=0.95,
        rationale="Done",
        original_recommendation_id="rec-2",
        priority="critical",
        severity="high",
        confidence=0.8,
        expected_impact="High impact",
        estimated_resolution_time="5m",
        required_resources=[],
        human_approval_requirement=True,
        suggested_operator_action="Evacuate",
        explanation="None"
    )

    prioritized = prioritizer.prioritize([item_low, item_critical])
    assert prioritized[0].priority == "critical"
    assert prioritized[1].priority == "low"

def test_risk_scorer() -> None:
    scorer = RiskScorer()
    
    # Nominal
    risk_low = scorer.calculate_risk(0.3, 0)
    assert risk_low == 0.1

    # Surged
    risk_high = scorer.calculate_risk(0.95, 2)
    assert risk_high == 0.80

def test_confidence_calculator() -> None:
    calc = ConfidenceCalculator()
    
    # High risk, low volunteers
    conf_low = calc.calculate_confidence(0.75, 5)
    assert conf_low == 0.70

    # Low risk, high volunteers
    conf_high = calc.calculate_confidence(0.1, 20)
    assert conf_high == 0.95

def test_history() -> None:
    history = DecisionHistory()
    res = DecisionEngineResult(
        confidence_score=0.95,
        rationale="Done",
        decisions=[],
        model_version="",
        execution_time_ms=0
    )
    
    history.record(res)
    assert len(history.get_all()) == 1
    
    history.clear()
    assert len(history.get_all()) == 0

@pytest.mark.asyncio
async def test_decision_engine(mock_orchestrator: MagicMock) -> None:
    rec_id = str(uuid4())
    expected_response = DecisionEngineResult(
        confidence_score=0.95,
        rationale="Done",
        decisions=[
            DecisionItem(
                confidence_score=0.95,
                rationale="Done",
                original_recommendation_id=rec_id,
                priority="high",
                severity="medium",
                confidence=0.0,
                expected_impact="Resolved bottleneck",
                estimated_resolution_time="12m",
                required_resources=["Volunteer Team Alpha"],
                human_approval_requirement=True,
                suggested_operator_action="Open auxiliary gate corridors",
                explanation="AI justified",
            )
        ],
        model_version="Gemini 2.5 Flash",
        execution_time_ms=15,
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_response)

    engine = DecisionEngine(mock_orchestrator)
    
    # Assert registry
    registered_prompt = mock_orchestrator.registry.get("decision_engine_agent", "latest")
    assert "You are the ATLAS Stadium Operations Decision Engine AI Agent." in registered_prompt.template

    context = DecisionContext(
        operational_state={"average_crowd_density": 0.85, "allocated_volunteers_count": 15},
        incidents=[{"id": "inc-1", "severity": "high", "resolved": False}],
        recommendations=[{"id": rec_id, "details": "Open Gate B"}]
    )

    # Act
    result = await engine.evaluate_decisions(context)

    # Assert
    assert len(result.decisions) == 1
    assert result.decisions[0].original_recommendation_id == rec_id
    assert result.decisions[0].confidence == 0.80  # risk: 0.1 + 0.4 (density 0.85 > 0.8) + 0.15 (incident count 1 * 0.15) = 0.65. conf: 0.95 - 0.15 (risk 0.65 > 0.6) = 0.80.
    mock_orchestrator.execute.assert_called_once()
