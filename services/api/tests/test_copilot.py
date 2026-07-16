import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, UTC
from fastapi.testclient import TestClient

from app.dependencies.container import ApplicationContainer
from app.application.operational_state.snapshot import OperationalSnapshot
from app.application.operational_state.state_manager import OperationalStateManager
from app.application.copilot import (
    ChatMessageDTO,
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotPrompt,
    CopilotService,
)
from app.intelligence import AIOrchestrator, PromptRegistry
from app.main import app

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
        active_incidents=[uuid4()],
        crowd_conditions={uuid4(): 0.3},
        recommendations=[uuid4()],
        volunteer_allocation={},
        queue_information={uuid4(): 5},
        stadium_health=0.9,
        timestamp=datetime.now(UTC),
    )
    state_manager.get_snapshot = AsyncMock(return_value=mock_snapshot)
    
    # Mock repositories for full memory context
    state_manager.incident_repo = MagicMock()
    state_manager.incident_repo.list = AsyncMock(return_value=[])
    state_manager.recommendation_repo = MagicMock()
    state_manager.recommendation_repo.list = AsyncMock(return_value=[])
    state_manager.state_repo = MagicMock()
    state_manager.state_repo.list = AsyncMock(return_value=[])
    
    return state_manager

def test_copilot_prompt() -> None:
    prompt = CopilotPrompt()
    assert prompt.metadata.name == "atlas_copilot_agent"
    assert "You are ATLAS Copilot" in prompt.get_version("v1").template

@pytest.mark.asyncio
async def test_copilot_service(mock_orchestrator: MagicMock, mock_state_manager: MagicMock) -> None:
    expected_response = CopilotChatResponse(
        confidence_score=0.95,
        rationale="Done",
        text="Hello user, everything is optimal.",
        citations=["[Incident #1]"],
        model_version="",
        execution_time_ms=0,
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_response)

    mock_event_repo = MagicMock()
    mock_event_repo.list = AsyncMock(return_value=[])

    service = CopilotService(mock_orchestrator, mock_state_manager, mock_event_repo)
    registered_prompt = mock_orchestrator.registry.get("atlas_copilot_agent", "latest")
    assert "You are ATLAS Copilot" in registered_prompt.template

    request = CopilotChatRequest(
        message="What is the stadium status?",
        history=[ChatMessageDTO(role="user", text="Hi")],
        language="English",
    )

    response = await service.chat(request)
    assert response.confidence_score == 0.95
    assert response.text == "Hello user, everything is optimal."
    assert response.model_version == "Gemini 2.5 Flash"
    assert response.execution_time_ms >= 0
    mock_state_manager.get_snapshot.assert_called_once()
    mock_orchestrator.execute.assert_called_once()

def test_copilot_chat_endpoint() -> None:
    client = TestClient(app)
    
    # Overwrite container dependencies to inject mock service
    container = app.state.container
    mock_service = MagicMock(spec=CopilotService)
    
    expected_response = CopilotChatResponse(
        confidence_score=0.9,
        rationale="Done",
        text="Mocked router response.",
        citations=[],
        model_version="Gemini 2.5 Flash",
        execution_time_ms=15,
    )
    mock_service.chat = AsyncMock(return_value=expected_response)
    
    # Use container overrides to inject mock copilot_service
    with container.copilot_service.override(mock_service):
        response = client.post(
            "/copilot/chat",
            json={
                "message": "Verify status",
                "history": [],
                "language": "French"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["text"] == "Mocked router response."
        assert data["data"]["confidence_score"] == 0.9
        mock_service.chat.assert_called_once()
