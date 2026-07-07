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
        executive_summary="Executive: Everything is running smoothly.",
        operations_summary="Operations: Queue wait times are under 10 minutes.",
        security_summary="Security: No active incidents reported.",
        medical_summary="Medical: Zero medical incidents.",
    )
    orchestrator.execute = AsyncMock(return_value=expected_response)

    agent = SituationSummaryAgent(orchestrator)

    # Verify prompt registry has it
    registered_prompt = registry.get("situation_summary_agent", "latest")
    assert "You are the ATLAS Stadium Operations Executive Summary AI Agent." in registered_prompt.template

    state_summary = {"zone_id": str(uuid4()), "density": 0.3}
    incidents: list[dict[str, Any]] = []
    crowd_conditions = {str(uuid4()): 0.3}
    volunteer_status = {"available": 5, "assigned": 2}
    recommendations: list[dict[str, Any]] = []

    # Act
    response = await agent.generate_summary(
        operational_state_summary=state_summary,
        incidents=incidents,
        crowd_conditions=crowd_conditions,
        volunteer_status=volunteer_status,
        recommendations=recommendations,
    )

    # Assert
    assert response.confidence_score == 0.95
    assert response.executive_summary == "Executive: Everything is running smoothly."
    assert response.security_summary == "Security: No active incidents reported."
    orchestrator.execute.assert_called_once()
