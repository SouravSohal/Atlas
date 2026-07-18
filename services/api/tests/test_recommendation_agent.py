from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.recommendations import (
    PrioritizedRecommendationItem,
    RecommendationAgent,
    RecommendationAgentResponse,
)
from app.intelligence import AIOrchestrator, PromptRegistry


@pytest.mark.asyncio
async def test_recommendation_agent_analysis() -> None:
    # Arrange
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry

    rec_id = str(uuid4())
    expected_response = RecommendationAgentResponse(
        confidence_score=0.95,
        rationale="High density and active security incident requires immediate gate opening.",
        natural_language_explanation="Operational state is degraded due to high queue wait times.",
        prioritized_recommendations=[
            PrioritizedRecommendationItem(
                recommendation_id=rec_id,
                action_type="OPEN_GATES",
                priority_order=1,
                priority_level="high",
                explanation="Opening gates immediately mitigates the queue waiting duration.",
            )
        ],
        risk_assessment="High risk of bottleneck congestion.",
        alternative_actions=["Deploy additional stewards to manually scan tickets."],
    )
    orchestrator.execute = AsyncMock(return_value=expected_response)

    agent = RecommendationAgent(orchestrator)

    # Verify prompt was registered during agent initialization
    registered_prompt = registry.get("recommendation_agent", "latest")
    assert "You are the ATLAS FIFA World Cup 2026 Stadium Operations AI Agent." in registered_prompt.template

    operational_state = {"zone_id": str(uuid4()), "density": 0.85, "queue_waiting_minutes": 25}
    incidents = [{"id": str(uuid4()), "type": "security", "severity": "high", "resolved": False}]
    business_recs = [{"id": rec_id, "action_type": "OPEN_GATES", "priority": "high"}]

    # Act
    response = await agent.analyze_recommendations(
        operational_state_summary=operational_state,
        incidents=incidents,
        business_recommendations=business_recs,
    )

    # Assert
    assert response.confidence_score == 0.95
    assert response.prioritized_recommendations[0].action_type == "OPEN_GATES"
    assert response.prioritized_recommendations[0].recommendation_id == rec_id
    assert response.alternative_actions == ["Deploy additional stewards to manually scan tickets."]
    orchestrator.execute.assert_called_once()
