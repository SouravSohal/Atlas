import json
from typing import Any, TypeVar
from uuid import UUID

import structlog
from pydantic import BaseModel, ValidationError

from app.intelligence.exceptions import ValidationException

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)


class ResponseValidator:
    """Validates LLM responses against JSON schema, required fields, and hallucination guards."""

    @staticmethod
    def validate(
        response_text: str,
        schema: type[T],
        allowed_entities: list[str] | None = None,
        min_confidence: float = 0.0,
    ) -> T:
        """Parses response_text to JSON and validates it against the Pydantic schema and guards."""
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error("Response is not valid JSON", text=response_text)
            raise ValidationException(f"Model response is not valid JSON: {e}") from e

        try:
            validated = schema.model_validate(parsed)
        except ValidationError as e:
            logger.error("JSON schema validation failed", json_data=parsed)
            raise ValidationException(f"JSON validation failed: {e}") from e

        if hasattr(validated, "confidence_score"):
            score = float(validated.confidence_score)
            if not (0.0 <= score <= 1.0):
                raise ValidationException("Model returned invalid confidence score (must be between 0.0 and 1.0).")
            if score < min_confidence:
                raise ValidationException(f"Confidence score {score} is below minimum allowed {min_confidence}.")

        if allowed_entities is not None:
            def check_strings(obj: Any) -> None:
                if isinstance(obj, str):
                    try:
                        # Validate UUID strings against trusted entities list
                        UUID(obj)
                        if obj not in allowed_entities:
                            raise ValidationException(f"Hallucination guard: Response referenced untrusted entity '{obj}'.")
                    except ValueError:
                        pass
                elif isinstance(obj, dict):
                    for v in obj.values():
                        check_strings(v)
                elif isinstance(obj, list):
                    for item in obj:
                        check_strings(item)

            check_strings(parsed)

        return validated
