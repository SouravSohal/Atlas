import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.intelligence.model_gateway import ModelGateway
from app.intelligence.stadium_orchestrator import StadiumAIOrchestrator, StadiumAIResponse


@pytest.mark.asyncio
async def test_stadium_orchestrator_briefing_generation():
    # 1. Setup mock gateway
    mock_gateway = MagicMock(spec=ModelGateway)
    
    mock_response_dict = {
        "executive_summary": "Aurelia Arena is operating at 65% capacity. Ingress flows are stable except Gate A.",
        "predictions": ["Crowd density at Gate A is predicted to exceed 85% by T-30m."],
        "explanation": "Reroute volunteers to Gate A to handle ticket scanning backpressure.",
        "risk_assessment": ["Gate A crowd backpressure may overflow into the Metro exit plaza."],
        "decision_justification": "Volunteer reallocations maximize ticket scanner validation rates."
    }
    
    mock_gateway.generate_response = AsyncMock(return_value=json.dumps(mock_response_dict))

    # 2. Instantiate Orchestrator
    orchestrator = StadiumAIOrchestrator(gateway=mock_gateway)

    # 3. Form input variables
    stadium_state = {"name": "Aurelia Arena", "capacity": 65000}
    active_incidents = [{"id": "inc-01", "type": "medical"}]
    telemetry = {"power_draw_mw": 8.2}
    recommendations = [{"action_type": "Reroute Volunteers"}]
    timeline = ["T-120m: Gates Open", "T-105m: Parking Inflow"]
    graph_summary = {"nodes_count": 10, "edges_count": 10}

    # 4. Generate briefing
    response = await orchestrator.generate_briefing(
        stadium_state=stadium_state,
        active_incidents=active_incidents,
        telemetry=telemetry,
        recommendations=recommendations,
        timeline=timeline,
        graph_summary=graph_summary
    )

    # 5. Assertions
    assert isinstance(response, StadiumAIResponse)
    assert response.executive_summary == "Aurelia Arena is operating at 65% capacity. Ingress flows are stable except Gate A."
    assert len(response.predictions) == 1
    assert "Gate A" in response.predictions[0]
    assert response.explanation == "Reroute volunteers to Gate A to handle ticket scanning backpressure."
    
    # Verify mock call parameters
    mock_gateway.generate_response.assert_called_once()
    call_args, call_kwargs = mock_gateway.generate_response.call_args
    assert call_kwargs["response_schema"] == StadiumAIResponse
    assert "[CURRENT STADIUM STATE]" in call_kwargs["prompt"]
    assert "[ACTIVE INCIDENTS]" in call_kwargs["prompt"]
    assert "[RECOMMENDATIONS TRIGGERED]" in call_kwargs["prompt"]
