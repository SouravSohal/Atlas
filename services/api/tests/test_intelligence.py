from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from app.intelligence import (
    AIOrchestrator,
    ContextRetriever,
    ModelGateway,
    PromptBuilder,
    PromptVersionManager,
    ResponseValidator,
)


class MockSchema(BaseModel):
    summary: str = Field(..., description="Summary of the context.")
    threat_level: str = Field(..., description="High, Medium, Low")

def test_prompt_version_manager() -> None:
    # Arrange
    manager = PromptVersionManager()

    # Act & Assert
    assert manager.get_template("default", "v1") == "Analyze the following context and return JSON: {context}"
    assert manager.get_template("default", "latest") == "Analyze the following context and return JSON: {context}"

    manager.register_template("test_prompt", "v1", "Template v1: {context}")
    manager.register_template("test_prompt", "v2", "Template v2: {context}")

    assert manager.get_template("test_prompt", "v1") == "Template v1: {context}"
    assert manager.get_template("test_prompt", "v2") == "Template v2: {context}"
    assert manager.get_template("test_prompt", "latest") == "Template v2: {context}"

    with pytest.raises(ValueError, match="not found"):
        manager.get_template("missing_prompt")

    with pytest.raises(ValueError, match="not found"):
        manager.get_template("test_prompt", "v3")

def test_prompt_builder() -> None:
    # Arrange
    template = "Hello {name}, your task is {task}."

    # Act
    prompt = PromptBuilder.build(template, name="Alice", task="coding")

    # Assert
    assert prompt == "Hello Alice, your task is coding."

    with pytest.raises(ValueError, match="Missing required parameter"):
        PromptBuilder.build(template, name="Alice")

def test_context_retriever() -> None:
    # Arrange
    context_dict = {"zone_id": "zone-123", "status": "active"}

    # Act
    str_context = ContextRetriever.format_context("raw text")
    dict_context = ContextRetriever.format_context(context_dict)

    # Assert
    assert str_context == "raw text"
    assert "zone_id" in dict_context
    assert "active" in dict_context

def test_response_validator() -> None:
    # Arrange
    valid_json = '{"summary": "Nothing to report", "threat_level": "Low"}'
    invalid_json = '{"summary": "Nothing to report", "threat_level": 123}'  # Invalid type for threat_level
    broken_json = '{"summary": "broken"'

    # Act
    parsed = ResponseValidator.validate(valid_json, MockSchema)

    # Assert
    assert parsed.summary == "Nothing to report"
    assert parsed.threat_level == "Low"

    with pytest.raises(ValueError, match="not valid JSON"):
        ResponseValidator.validate(broken_json, MockSchema)

    with pytest.raises(ValueError, match="Schema validation failed"):
        ResponseValidator.validate(invalid_json, MockSchema)

@pytest.mark.asyncio
async def test_model_gateway() -> None:
    # Arrange
    # Patch genai.Client so it doesn't try to access Google Cloud or check credentials
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Mock async generate_content call
        mock_resp = MagicMock()
        mock_resp.text = '{"summary": "Gate Breach", "threat_level": "High"}'
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)

        gateway = ModelGateway(api_key="mock_key")

        # Act
        response_text = await gateway.generate_response(
            prompt="Analyze this",
            model="gemini-2.5-pro",
        )

        # Assert
        assert response_text == '{"summary": "Gate Breach", "threat_level": "High"}'
        mock_client.aio.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_ai_orchestrator_execution() -> None:
    # Arrange
    gateway = MagicMock(spec=ModelGateway)
    gateway.generate_response = AsyncMock(
        return_value='{"summary": "Crowd surge in Zone B", "threat_level": "Medium"}'
    )

    version_manager = PromptVersionManager()
    version_manager.register_template("analyze_threat", "v1", "Analyze: {context}")

    orchestrator = AIOrchestrator(gateway, version_manager)

    # Act
    result = await orchestrator.execute(
        prompt_name="analyze_threat",
        prompt_version="v1",
        context_data={"zone": "Zone B", "crowd": "dense"},
        schema=MockSchema,
    )

    # Assert
    assert isinstance(result, MockSchema)
    assert result.summary == "Crowd surge in Zone B"
    assert result.threat_level == "Medium"
    gateway.generate_response.assert_called_once()
