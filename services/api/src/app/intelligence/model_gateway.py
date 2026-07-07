from typing import Any

import structlog
from google import genai
from google.genai import types
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

class ModelGateway:
    """Gateway to execute raw calls to Gemini API with retry and logging mechanisms."""

    def __init__(self, api_key: str | None = None) -> None:
        # If api_key is None, genai.Client() automatically checks the GEMINI_API_KEY environment variable.
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_response(
        self,
        prompt: str,
        model: str = "gemini-2.5-pro",
        response_schema: type | None = None,
        tools: list[Any] | None = None,
    ) -> str:
        """Calls Gemini API using google-genai client with retries and structured logging."""
        logger.info(
            "Sending request to Gemini API",
            model=model,
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

        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        text = response.text
        if text is None:
            raise ValueError("Gemini API returned an empty response text.")

        return text
