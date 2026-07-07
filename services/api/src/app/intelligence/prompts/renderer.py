import json
from typing import Any

from pydantic import BaseModel


class PromptRenderer:
    """Handles rendering of prompt templates, context injection, schema injection, and function definitions."""

    @staticmethod
    def render_schema(schema: type[BaseModel]) -> str:
        """Generates a JSON schema string representation of a Pydantic model for injection."""
        return json.dumps(schema.model_json_schema(), indent=2)

    @staticmethod
    def render_functions(functions: list[dict[str, Any]]) -> str:
        """Formats function/tool definitions into a readable string for model context."""
        return json.dumps(functions, indent=2)

    @staticmethod
    def compile(
        template_content: str,
        variables: dict[str, Any],
        context: str | None = None,
        schema: type[BaseModel] | None = None,
        functions: list[dict[str, Any]] | None = None,
    ) -> str:
        """Compiles the final prompt string with template parameters, context, schema, and function calls."""
        try:
            rendered = template_content.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing required parameter '{e.args[0]}' for prompt template rendering.") from e
        except Exception as e:
            raise ValueError(f"Failed to render prompt template: {e}") from e

        sections = [rendered]
        if context:
            sections.append(f"[CONTEXT]\n{context}")
        if schema:
            schema_str = PromptRenderer.render_schema(schema)
            sections.append(f"[RESPONSE SCHEMA]\n{schema_str}")
        if functions:
            func_str = PromptRenderer.render_functions(functions)
            sections.append(f"[AVAILABLE FUNCTIONS]\n{func_str}")

        return "\n\n".join(sections)
