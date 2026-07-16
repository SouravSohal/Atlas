from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.operational_state import (
    SituationSummaryAgent,
    SituationSummaryAgentResponse,
)
from app.intelligence import AIOrchestrator, PromptRegistry


@pytest.mark.asyncio
async def test_situation_summary_agent() -> None:
    # Arrange
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry

    expected_response = SituationSummaryAgentResponse(
        confidence_score=0.95,
        rationale="Completed compile of operations telemetry.",
        executive_summary="Everything is running smoothly.",
        situation_assessment="Stadium operations are nominal across all zones.",
        immediate_risks=["Potential gate bottleneck if influx surges"],
        recommended_actions=["Deploy auxiliary gates"],
        predicted_outcome="Density will drop within 10 minutes",
        assumptions=["Volunteer attendance remains stable"],
        alternative_strategies=["Deploy safety guides to gate corridors"],
    )
    orchestrator.execute = AsyncMock(return_value=expected_response)

    agent = SituationSummaryAgent(orchestrator)

    # Verify prompt registry has it
    registered_prompt = registry.get("situation_summary_agent", "latest")
    assert "You are the ATLAS Stadium Operations Situation Analysis Engine." in registered_prompt.template

    state = {"zone_id": str(uuid4()), "density": 0.3}
    incidents: list[dict[str, Any]] = []
    telemetry = {"crowd_density": 0.3, "queue_lengths": 10}
    weather = "Sunny, 24C"
    recommendations: list[dict[str, Any]] = []
    timeline = ["Match started"]

    # Act
    response = await agent.generate_summary(
        operational_state=state,
        incidents=incidents,
        telemetry=telemetry,
        weather=weather,
        recommendations=recommendations,
        timeline=timeline,
    )

    # Assert
    assert response.confidence_score == 0.95
    assert response.executive_summary == "Everything is running smoothly."
    assert response.situation_assessment == "Stadium operations are nominal across all zones."
    orchestrator.execute.assert_called_once()
