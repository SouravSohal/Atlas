import json
from typing import Any, TypeVar, overload

import structlog
from pydantic import BaseModel

from app.intelligence.context_retriever import ContextRetriever
from app.intelligence.model_gateway import ModelGateway
from app.intelligence.prompt_builder import PromptBuilder
from app.intelligence.prompt_registry import PromptRegistry
from app.intelligence.response_validator import ResponseValidator

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)


class AIOrchestrator:
    """The central orchestrator for building prompts, retrieving context, calling model, and validating responses."""

    def __init__(
        self,
        gateway: ModelGateway,
        registry: PromptRegistry,
        context_retriever: ContextRetriever,
    ) -> None:
        self.gateway = gateway
        self.registry = registry
        self.context_retriever = context_retriever

    @overload
    async def execute(
        self,
        prompt_name: str,
        prompt_version: str = "latest",
        context_zone_id: Any | None = None,
        schema: None = None,
        tools: list[Any] | None = None,
        model: str | None = None,
        constraints: list[str] | None = None,
        allowed_entities: list[str] | None = None,
        min_confidence: float = 0.0,
        **prompt_vars: Any,
    ) -> str:
        ...

    @overload
    async def execute(
        self,
        prompt_name: str,
        prompt_version: str,
        context_zone_id: Any | None,
        schema: type[T],
        tools: list[Any] | None = None,
        model: str | None = None,
        constraints: list[str] | None = None,
        allowed_entities: list[str] | None = None,
        min_confidence: float = 0.0,
        **prompt_vars: Any,
    ) -> T:
        ...

    @overload
    async def execute(
        self,
        prompt_name: str,
        prompt_version: str = "latest",
        context_zone_id: Any | None = None,
        *,
        schema: type[T],
        tools: list[Any] | None = None,
        model: str | None = None,
        constraints: list[str] | None = None,
        allowed_entities: list[str] | None = None,
        min_confidence: float = 0.0,
        **prompt_vars: Any,
    ) -> T:
        ...

    async def execute(
        self,
        prompt_name: str,
        prompt_version: str = "latest",
        context_zone_id: Any | None = None,
        schema: type[BaseModel] | None = None,
        tools: list[Any] | None = None,
        model: str | None = None,
        constraints: list[str] | None = None,
        allowed_entities: list[str] | None = None,
        min_confidence: float = 0.0,
        **prompt_vars: Any,
    ) -> Any:
        """Orchestrates the entire AI pipeline: building prompt, retrieving context, calling model, and validation."""
        target_model = model or self.gateway.default_model
        logger.info(
            "Executing AI Orchestrator pipeline",
            prompt_name=prompt_name,
            version=prompt_version,
            model=target_model,
            has_schema=schema is not None,
        )

        prompt_ver = self.registry.get(prompt_name, prompt_version)

        context_str = ""
        if context_zone_id is not None:
            context_data = await self.context_retriever.retrieve_zone_context(context_zone_id)
            context_str = json.dumps(context_data, indent=2, default=str)

        final_prompt = PromptBuilder.build(
            template=prompt_ver.template,
            context=context_str,
            constraints=constraints,
            schema_instructions=schema.__doc__ if schema else None,
            **prompt_vars,
        )

        raw_response = await self.gateway.generate_response(
            prompt=final_prompt,
            model=target_model,
            response_schema=schema,
            tools=tools,
        )

        if schema is not None:
            return ResponseValidator.validate(
                response_text=raw_response,
                schema=schema,
                allowed_entities=allowed_entities,
                min_confidence=min_confidence,
            )

        return raw_response
