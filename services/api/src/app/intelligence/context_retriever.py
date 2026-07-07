import json
from typing import Any


class ContextRetriever:
    """Formats raw domain entity context, snapshots, or lists into standardized text representations."""

    @staticmethod
    def format_context(context_data: dict[str, Any] | list[Any] | str) -> str:
        """Converts raw context data into a clean text block."""
        if isinstance(context_data, str):
            return context_data
        try:
            return json.dumps(context_data, indent=2, default=str)
        except Exception as e:
            raise ValueError(f"Failed to serialize context data: {e}") from e
