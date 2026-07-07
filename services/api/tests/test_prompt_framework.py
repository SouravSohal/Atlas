import pytest
from pydantic import Field

from app.intelligence.prompts import (
    BasePrompt,
    PromptMetadata,
    PromptRenderer,
    PromptTemplate,
    PromptVariables,
    PromptVersion,
)


class MockVariables(PromptVariables):
    task_name: str = Field(..., description="Name of the task.")
    priority: str = Field(default="low", description="Priority level.")


def test_base_prompt_and_metadata() -> None:
    # Arrange
    meta = PromptMetadata(
        name="test_prompt",
        description="A simple testing prompt.",
        author="System Admin",
        tags=["test", "unit-test"],
    )
    v1 = PromptVersion(version="v1", template="Hello {task_name}", description="V1 template")
    v2 = PromptVersion(version="v2", template="Task details: {task_name} with priority {priority}", description="V2 template")

    # Act
    prompt = BasePrompt(metadata=meta, versions=[v1, v2])

    # Assert
    assert prompt.metadata.name == "test_prompt"
    assert prompt.get_version("v1") == v1
    assert prompt.get_version("v2") == v2
    assert prompt.get_version("latest") == v2

    with pytest.raises(ValueError, match="not found"):
        prompt.get_version("v3")

    empty_prompt = BasePrompt(metadata=meta, versions=[])
    with pytest.raises(ValueError, match="No versions registered"):
        empty_prompt.get_version("latest")


def test_prompt_template_render() -> None:
    # Arrange
    tpl = PromptTemplate("Execute task {task_name} at level {priority}")

    # Act
    rendered = tpl.render(task_name="deploy", priority="high")

    # Assert
    assert rendered == "Execute task deploy at level high"

    with pytest.raises(ValueError, match="Missing required parameter"):
        tpl.render(task_name="deploy")


def test_prompt_variables_instantiation() -> None:
    # Arrange & Act
    vars_instance = MockVariables(task_name="backup")

    # Assert
    assert vars_instance.task_name == "backup"
    assert vars_instance.priority == "low"


def test_prompt_renderer_compile() -> None:
    # Arrange
    from pydantic import BaseModel

    class DummySchema(BaseModel):
        success: bool

    functions = [{
        "name": "dispatch_task",
        "description": "Dispatches a volunteer to a task",
        "parameters": {"type": "object", "properties": {"task_id": {"type": "string"}}},
    }]

    # Act
    compiled = PromptRenderer.compile(
        template_content="Render {task_name}",
        variables={"task_name": "clean_up"},
        context="stadium context",
        schema=DummySchema,
        functions=functions,
    )

    # Assert
    assert "Render clean_up" in compiled
    assert "[CONTEXT]\nstadium context" in compiled
    assert "[RESPONSE SCHEMA]" in compiled
    assert "DummySchema" in compiled
    assert "[AVAILABLE FUNCTIONS]" in compiled
    assert "dispatch_task" in compiled
