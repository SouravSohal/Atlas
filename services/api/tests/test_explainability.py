from unittest.mock import AsyncMock, MagicMock

import pytest

from app.intelligence import AIOrchestrator, PromptRegistry
from app.intelligence.explainability import (
    AlternativeGenerator,
    ConfidenceAnalyzer,
    EvidenceCollector,
    ExplainabilityEngine,
    ReasoningBuilder,
    RecommendationExplanation,
)


# Simulated domain objects for testing
class MockRecommendation:
    def __init__(self, action_type: str, priority: str, details: str) -> None:
        self.action_type = action_type
        self.priority = priority
        self.details = details

class MockOverview:
    def __init__(self, volunteers: int) -> None:
        self.allocated_volunteers_count = volunteers

class MockState:
    def __init__(self, density: float, queue: int) -> None:
        self.density = density
        self.queue_waiting_minutes = queue

class MockIncident:
    def __init__(self, severity: str, description: str, resolved: bool) -> None:
        self.severity = severity
        self.description = description
        self.resolved = resolved

@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

def test_evidence_collector() -> None:
    collector = EvidenceCollector()
    overview = MockOverview(12)
    state = MockState(0.7, 10)
    incidents = [MockIncident("high", "Congestion gate A", False)]

    evidence = collector.collect(overview, state, incidents)
    assert len(evidence) == 4
    assert "Found 1 active incidents" in evidence[0]
    assert "Zone crowd density is at 70%" in evidence[2]

    empty_evidence = collector.collect(None, None, [])
    assert "No active incidents logged." in empty_evidence[0]

def test_confidence_analyzer() -> None:
    analyzer = ConfidenceAnalyzer()
    
    # Base nominal scenario
    conf_nominal = analyzer.calculate(0.3, 15, 0)
    assert conf_nominal == 0.95

    # Degraded scenarios
    conf_degraded = analyzer.calculate(0.9, 5, 3)
    assert conf_degraded == 0.6

def test_reasoning_builder() -> None:
    builder = ReasoningBuilder()
    rules = builder.build_business_rules(0.85, 20)
    assert len(rules) == 3
    assert "Rule #CrowdRedThreshold" in rules[1]
    assert "Rule #QueueBottleneck" in rules[2]

def test_alternative_generator() -> None:
    generator = AlternativeGenerator()
    
    alts_reroute = generator.generate("reroute spectators")
    assert "Hold crowd at current gate entrances" in alts_reroute

    alts_dispatch = generator.generate("dispatch volunteer team")
    assert "Deploy static security personnel" in alts_dispatch

    alts_default = generator.generate("inspect cameras")
    assert "Maintain status quo operations" in alts_default

@pytest.mark.asyncio
async def test_explainability_engine(mock_orchestrator: MagicMock) -> None:
    expected_response = RecommendationExplanation(
        confidence_score=0.96,
        rationale="Justified.",
        why_recommendation="Egress queue is too long.",
        evidence_considered=["Bottleneck active"],
        business_rules_triggered=[],
        operational_data_used=[],
        confidence=0.0,
        alternative_actions=[],
        trade_offs=["Increased staffing cost"],
        limitations=["Temporary fix"],
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_response)

    engine = ExplainabilityEngine(mock_orchestrator)
    
    # Assert registry
    registered_prompt = mock_orchestrator.registry.get("explainability_agent", "latest")
    assert "You are the ATLAS Stadium Operations AI Explainability Agent." in registered_prompt.template

    rec = MockRecommendation("reroute", "high", "Divert incoming crowd")
    overview = MockOverview(15)
    state = MockState(0.85, 20)
    incidents = [MockIncident("critical", "Gate failure", False)]

    # Act
    explanation = await engine.explain(rec, overview, state, incidents)

    # Assert
    assert explanation.why_recommendation == "Egress queue is too long."
    assert explanation.confidence == 0.85
    assert "Rule #CrowdRedThreshold: density exceeded 80%" in explanation.business_rules_triggered
    mock_orchestrator.execute.assert_called_once()
