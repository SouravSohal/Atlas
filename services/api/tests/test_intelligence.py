from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import BaseModel, Field

from app.intelligence import (
    AIOrchestrator,
    ContextRetriever,
    ModelGateway,
    PromptBuilder,
    PromptNotFoundException,
    PromptRegistry,
    ResponseValidator,
    ValidationException,
)


class MockSchema(BaseModel):
    summary: str = Field(..., description="Summary of the context.")
    threat_level: str = Field(..., description="High, Medium, Low")
    confidence_score: float = Field(..., ge=0.0, le=1.0)


def test_prompt_registry() -> None:
    # Arrange
    registry = PromptRegistry()

    # Act & Assert
    registry.register("analyze_threat", "v1", "Analyze: {context}", "First version")
    registry.register("analyze_threat", "v2", "Analyze version 2: {context}", "Second version")

    assert registry.get("analyze_threat", "v1").template == "Analyze: {context}"
    assert registry.get("analyze_threat", "v2").template == "Analyze version 2: {context}"
    assert registry.get("analyze_threat", "latest").template == "Analyze version 2: {context}"

    with pytest.raises(PromptNotFoundException, match="is not registered"):
        registry.get("missing_prompt")

    with pytest.raises(PromptNotFoundException, match="not found"):
        registry.get("analyze_threat", "v3")


def test_prompt_builder() -> None:
    # Arrange
    template = "Hello {name}, your task is {task}."

    # Act
    prompt = PromptBuilder.build(
        template=template,
        context="Sample context",
        constraints=["constraint A", "constraint B"],
        schema_instructions="instructions",
        name="Alice",
        task="coding",
    )

    # Assert
    assert "Hello Alice, your task is coding." in prompt
    assert "[OPERATIONAL CONTEXT]\nSample context" in prompt
    assert "[CONSTRAINTS]\n- constraint A\n- constraint B" in prompt
    assert "[SCHEMA INSTRUCTIONS]\ninstructions" in prompt

    with pytest.raises(ValueError, match="Missing required parameter"):
        PromptBuilder.build(template, context="Sample context", name="Alice")


@pytest.mark.asyncio
async def test_context_retriever() -> None:
    # Arrange
    state_repo = MagicMock()
    incident_repo = MagicMock()
    rec_repo = MagicMock()

    # mock values
    mock_state = MagicMock()
    mock_state.density.value = 0.8
    mock_state.queue_estimate.waiting_minutes = 15
    state_repo.get_by_id = AsyncMock(return_value=mock_state)

    mock_inc = MagicMock()
    mock_inc.id = uuid4()
    mock_inc.incident_type.value = "security"
    mock_inc.severity.value = "high"
    mock_inc.description = "breach"
    mock_inc.resolved = False
    incident_repo.list = AsyncMock(return_value=[mock_inc])

    mock_rec = MagicMock()
    mock_rec.id = uuid4()
    mock_rec.action_type = "reroute"
    mock_rec.priority.value = "high"
    mock_rec.status.value = "pending"
    rec_repo.list = AsyncMock(return_value=[mock_rec])

    retriever = ContextRetriever(state_repo, incident_repo, rec_repo)
    zone_id = uuid4()

    # Act
    context = await retriever.retrieve_zone_context(zone_id)

    # Assert
    assert context["operational_state"]["density"] == 0.8
    assert context["operational_state"]["queue_waiting_minutes"] == 15
    assert context["incidents"][0]["description"] == "breach"
    assert context["recommendations"][0]["action_type"] == "reroute"


def test_response_validator() -> None:
    # Arrange
    valid_json = '{"summary": "Nothing to report", "threat_level": "Low", "confidence_score": 0.9}'
    invalid_json = '{"summary": "Nothing to report", "threat_level": 123, "confidence_score": 0.9}'
    broken_json = '{"summary": "broken"'
    low_confidence_json = '{"summary": "Nothing to report", "threat_level": "Low", "confidence_score": 0.3}'

    # Act
    parsed = ResponseValidator.validate(valid_json, MockSchema, min_confidence=0.5)

    # Assert
    assert parsed.summary == "Nothing to report"
    assert parsed.confidence_score == 0.9

    with pytest.raises(ValidationException, match="is not valid JSON"):
        ResponseValidator.validate(broken_json, MockSchema)

    with pytest.raises(ValidationException, match="JSON validation failed"):
        ResponseValidator.validate(invalid_json, MockSchema)

    with pytest.raises(ValidationException, match="below minimum allowed"):
        ResponseValidator.validate(low_confidence_json, MockSchema, min_confidence=0.8)


def test_response_validator_hallucination_guard() -> None:
    # Arrange
    allowed_id = str(uuid4())
    untrusted_id = str(uuid4())
    response_json = f'{{"summary": "Breach at gate", "threat_level": "High", "confidence_score": 0.95, "entity_id": "{untrusted_id}"}}'

    class EntitySchema(MockSchema):
        entity_id: str

    # Act & Assert
    # Passing with allowed ID
    allowed_json = f'{{"summary": "Breach at gate", "threat_level": "High", "confidence_score": 0.95, "entity_id": "{allowed_id}"}}'
    parsed = ResponseValidator.validate(allowed_json, EntitySchema, allowed_entities=[allowed_id])
    assert parsed.entity_id == allowed_id

    # Failing with untrusted ID
    with pytest.raises(ValidationException, match="Hallucination guard"):
        ResponseValidator.validate(response_json, EntitySchema, allowed_entities=[allowed_id])


@pytest.mark.asyncio
async def test_model_gateway() -> None:
    # Arrange
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.text = '{"summary": "Gate Breach", "threat_level": "High", "confidence_score": 0.9}'
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)

        gateway = ModelGateway(api_key="mock_key")

        # Act
        response_text = await gateway.generate_response(
            prompt="Analyze this",
            model="gemini-2.5-flash",
        )

        # Assert
        assert response_text == '{"summary": "Gate Breach", "threat_level": "High", "confidence_score": 0.9}'
        mock_client.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_ai_orchestrator_execution() -> None:
    # Arrange
    gateway = MagicMock(spec=ModelGateway)
    gateway.generate_response = AsyncMock(
        return_value='{"summary": "Crowd surge in Zone B", "threat_level": "Medium", "confidence_score": 0.95}'
    )

    registry = PromptRegistry()
    registry.register("analyze_threat", "v1", "Analyze: {context}")

    state_repo = MagicMock()
    incident_repo = MagicMock()
    rec_repo = MagicMock()

    mock_state = MagicMock()
    mock_state.density.value = 0.8
    mock_state.queue_estimate.waiting_minutes = 15
    state_repo.get_by_id = AsyncMock(return_value=mock_state)
    incident_repo.list = AsyncMock(return_value=[])
    rec_repo.list = AsyncMock(return_value=[])

    retriever = ContextRetriever(state_repo, incident_repo, rec_repo)

    orchestrator = AIOrchestrator(gateway, registry, retriever)
    zone_id = uuid4()

    # Act
    result = await orchestrator.execute(
        prompt_name="analyze_threat",
        prompt_version="v1",
        context_zone_id=zone_id,
        schema=MockSchema,
        min_confidence=0.8,
    )

    # Assert
    assert isinstance(result, MockSchema)
    assert result.summary == "Crowd surge in Zone B"
    assert result.threat_level == "Medium"
    assert result.confidence_score == 0.95
    gateway.generate_response.assert_called_once()
