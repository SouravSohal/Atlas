from typing import Any

import structlog
from google import genai
from google.genai import types
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.intelligence.exceptions import ModelGatewayException

logger = structlog.get_logger()


class ModelGateway:
    """Gateway to execute raw calls to Gemini API with retry and logging mechanisms."""

    def __init__(self, api_key: str | None = None, default_model: str = "gemini-2.5-pro") -> None:
        import os
        actual_key = None
        if isinstance(api_key, str) and api_key.strip():
            actual_key = api_key
        else:
            actual_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI__API_KEY")

        if actual_key:
            self.client = genai.Client(api_key=actual_key)
        else:
            self.client = genai.Client()
        self.default_model = default_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_response(
        self,
        prompt: str,
        model: str | None = None,
        response_schema: type | None = None,
        tools: list[Any] | None = None,
    ) -> str:
        """Calls Gemini API using google-genai client with retries and structured logging."""
        target_model = model or self.default_model
        logger.info(
            "Sending request to Gemini API",
            model=target_model,
            prompt_length=len(prompt),
            has_schema=response_schema is not None,
            has_tools=tools is not None,
        )

        config_args: dict[str, Any] = {
            "response_mime_type": "application/json",
        }

        if response_schema is not None:
            config_args["response_schema"] = response_schema

        if tools is not None:
            config_args["tools"] = tools

        config = types.GenerateContentConfig(**config_args)

        try:
            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config,
            )
        except Exception as e:
            logger.error("Gemini API invocation failed", error=str(e))
            raise ModelGatewayException(f"Gemini API invocation failed: {e}") from e

        text = response.text
        if text is None:
            raise ModelGatewayException("Gemini API returned an empty response text.")

        return text
