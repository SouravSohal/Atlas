import pytest
from pydantic import ValidationError

from app.intelligence.structured_output import (
    AIExplanation,
    AIPrediction,
    AIRecommendation,
    AIResponse,
    AISummary,
    ResponseEnvelope,
)


def test_ai_response_validation() -> None:
    # Arrange & Act
    response = AIResponse(confidence_score=0.85, rationale="Valid rationale")

    # Assert
    assert response.confidence_score == 0.85
    assert response.rationale == "Valid rationale"

    # Invalid confidence score > 1.0
    with pytest.raises(ValidationError):
        AIResponse(confidence_score=1.2, rationale="Invalid score")

    # Invalid confidence score < 0.0
    with pytest.raises(ValidationError):
        AIResponse(confidence_score=-0.1, rationale="Invalid score")


def test_structured_response_subclasses() -> None:
    # 1. Recommendation
    rec = AIRecommendation(
        confidence_score=0.9,
        rationale="Density threshold reached",
        action_type="REROUTE_CROWD",
        priority="high",
        details="Reroute through Gate C",
    )
    assert rec.action_type == "REROUTE_CROWD"

    # 2. Explanation
    exp = AIExplanation(
        confidence_score=0.8,
        rationale="Anomalous wait times",
        root_cause="Gate closure",
        impact_analysis="Severe queue backups",
        mitigation_steps=["Open backup gates", "Deploy volunteers"],
    )
    assert exp.root_cause == "Gate closure"
    assert "Open backup gates" in exp.mitigation_steps

    # 3. Summary
    summ = AISummary(
        confidence_score=0.95,
        rationale="Aggregated telemetry",
        summary="Sector A status normal",
        key_points=["Density 0.4", "Zero active incidents"],
        threat_level="low",
    )
    assert summ.threat_level == "low"

    # 4. Prediction
    pred = AIPrediction(
        confidence_score=0.75,
        rationale="Based on arrival rate",
        predicted_value="Congested in 15 minutes",
        probability=0.8,
        time_horizon="15m",
    )
    assert pred.probability == 0.8


def test_response_envelope() -> None:
    # Arrange
    rec = AIRecommendation(
        confidence_score=0.9,
        rationale="Density threshold reached",
        action_type="REROUTE_CROWD",
        priority="high",
        details="Reroute through Gate C",
    )

    envelope = ResponseEnvelope[AIRecommendation](
        trace_id="trace-1234",
        model_name="gemini-2.5-pro",
        prompt_version="v1.2.0",
        execution_time_ms=125.5,
        data=rec,
    )

    # Act
    serialized = envelope.model_dump()

    # Assert
    assert serialized["trace_id"] == "trace-1234"
    assert serialized["data"]["action_type"] == "REROUTE_CROWD"
    assert serialized["execution_time_ms"] == 125.5
