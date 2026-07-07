from typing import Any, TypeVar, overload

import structlog
from pydantic import BaseModel

from app.intelligence.context_retriever import ContextRetriever
from app.intelligence.model_gateway import ModelGateway
from app.intelligence.prompt_builder import PromptBuilder
from app.intelligence.prompt_version_manager import PromptVersionManager
from app.intelligence.response_validator import ResponseValidator

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class AIOrchestrator:
    """The central orchestrator for building prompts, retrieving context, calling model, and validating responses."""

    def __init__(
        self,
        gateway: ModelGateway,
        version_manager: PromptVersionManager,
    ) -> None:
        self.gateway = gateway
        self.version_manager = version_manager

    @overload
    async def execute(
        self,
        prompt_name: str,
        prompt_version: str = "latest",
        context_data: Any | None = None,
        schema: None = None,
        tools: list[Any] | None = None,
        model: str = "gemini-2.5-pro",
        **prompt_vars: Any,
    ) -> str:
        ...

    @overload
    async def execute(
        self,
        prompt_name: str,
        prompt_version: str,
        context_data: Any | None,
        schema: type[T],
        tools: list[Any] | None = None,
        model: str = "gemini-2.5-pro",
        **prompt_vars: Any,
    ) -> T:
        ...

    @overload
    async def execute(
        self,
        prompt_name: str,
        prompt_version: str = "latest",
        context_data: Any | None = None,
        *,
        schema: type[T],
        tools: list[Any] | None = None,
        model: str = "gemini-2.5-pro",
        **prompt_vars: Any,
    ) -> T:
        ...

    async def execute(
        self,
        prompt_name: str,
        prompt_version: str = "latest",
        context_data: Any | None = None,
        schema: type[BaseModel] | None = None,
        tools: list[Any] | None = None,
        model: str = "gemini-2.5-pro",
        **prompt_vars: Any,
    ) -> Any:
        """Orchestrates the entire AI pipeline: building prompt, retrieving context, calling model, and validation.

        If schema is provided, returns validated Pydantic model. Else, returns raw JSON/text string.
        """
        logger.info(
            "Executing AI Orchestrator pipeline",
            prompt_name=prompt_name,
            version=prompt_version,
            model=model,
            has_schema=schema is not None,
        )

        # 1. Fetch template
        template = self.version_manager.get_template(prompt_name, prompt_version)

        # 2. Format context
        context_str = ""
        if context_data is not None:
            context_str = ContextRetriever.format_context(context_data)

        # 3. Build Prompt
        final_prompt = PromptBuilder.build(template, context=context_str, **prompt_vars)

        # 4. Generate Response
        raw_response = await self.gateway.generate_response(
            prompt=final_prompt,
            model=model,
            response_schema=schema,
            tools=tools,
        )

        # 5. Validate if schema provided
        if schema is not None:
            return ResponseValidator.validate(raw_response, schema)

        return raw_response
