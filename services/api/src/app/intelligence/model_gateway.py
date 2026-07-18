from typing import Any

import structlog
from google import genai
from google.genai import types
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.intelligence.exceptions import ModelGatewayException

logger = structlog.get_logger()


class ModelGateway:
    """Gateway to execute raw calls to Gemini API with retry and logging mechanisms."""
    default_model: str = "gemini-2.5-flash"

    def __init__(self, api_key: str | None = None, default_model: str = "gemini-2.5-flash") -> None:
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
        """Calls Gemini API using google-genai client with retries, fallback models, and logging."""
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

        # Build fallback model chain to prevent 429 quota exhaustion from failing operations
        models_to_try = [target_model]
        fallbacks = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"]
        for fb in fallbacks:
            if fb != target_model:
                models_to_try.append(fb)

        last_error = None
        for current_model in models_to_try:
            try:
                response = await self.client.aio.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=config,
                )
                text = response.text
                if text is not None:
                    return text
                logger.warning("Gemini API returned an empty response text, attempting next model in chain.", model=current_model)
            except Exception as e:
                last_error = e
                logger.warning(
                    "Gemini API invocation failed, attempting model fallback",
                    attempted_model=current_model,
                    error=str(e)
                )

        error_msg = f"All Gemini API models failed in fallback chain. Last error: {last_error}"
        logger.error(error_msg)
        raise ModelGatewayException(error_msg) from last_error
