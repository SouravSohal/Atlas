from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.recommendations import (
    AIRecommendationGenerator,
    AIRecommendationGeneratorResponse,
)
from app.application.recommendations.generator import AIRecommendationItem
from app.intelligence import AIOrchestrator, PromptRegistry


@pytest.mark.asyncio
async def test_recommendation_generator() -> None:
    # Arrange
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry

    expected_response = AIRecommendationGeneratorResponse(
        confidence_score=0.95,
        rationale="Analyzing operations indicators.",
        recommendations=[
            AIRecommendationItem(
                action_type="Reroute Volunteers to Ingress Gate 1",
                priority="high",
                confidence=0.95,
                why="Turnstile queue waiting time exceeds the nominal threshold of 10 minutes at Ingress Gate 1.",
                evidence="Telemetry reports wait time of 15.0 minutes.",
                operational_data_used=["average_queue_wait_minutes"],
                alternative_actions=["Direct spectators to Gate 2", "Manual ticket list validation"],
                trade_offs="Reduces staff availability at information kiosks.",
                explanation="Turnstile queue waiting time exceeds the nominal threshold of 10 minutes at Ingress Gate 1.",
                estimated_impact="Decrease queue wait time by 5 minutes.",
                estimated_recovery_time_minutes=15,
                operational_reasoning="Average turnstile queue length is high based on latest telemetry.",
            )
        ]
    )
    orchestrator.execute = AsyncMock(return_value=expected_response)

    agent = AIRecommendationGenerator(orchestrator)

    # Verify prompt registry has it
    registered_prompt = registry.get("ai_recommendation_generator", "latest")
    assert "You are the ATLAS FIFA World Cup 2026 Smart Stadium Operations AI Recommendation Engine." in registered_prompt.template

    telemetry = {"average_crowd_density": 0.45, "average_queue_wait_minutes": 15.0}
    incidents: list[dict[str, Any]] = []
    state = {"stadium_health": 0.95, "zones_count": 8}

    # Act
    response = await agent.generate_recommendations(
        telemetry=telemetry,
        incidents=incidents,
        operational_state=state,
    )

    # Assert
    assert len(response.recommendations) == 1
    rec = response.recommendations[0]
    assert rec.action_type == "Reroute Volunteers to Ingress Gate 1"
    assert rec.priority == "high"
    assert rec.confidence == 0.95
    assert rec.estimated_recovery_time_minutes == 15
