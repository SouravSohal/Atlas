import json
from typing import TypeVar

import structlog
from pydantic import BaseModel, ValidationError

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

class ResponseValidator:
    """Validates and parses JSON responses from the Gemini API against a Pydantic schema."""

    @staticmethod
    def validate(response_text: str, schema: type[T]) -> T:
        """Parses response_text to JSON and validates it against the Pydantic schema."""
        try:
            parsed_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse response text as JSON", text=response_text)
            raise ValueError(f"Model response is not valid JSON: {e}") from e

        try:
            return schema.model_validate(parsed_json)
        except ValidationError as e:
            logger.error("JSON validation against schema failed", json_data=parsed_json)
            raise ValueError(f"Schema validation failed: {e}") from e
