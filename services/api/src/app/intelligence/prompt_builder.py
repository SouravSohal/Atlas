from typing import Any


class PromptBuilder:
    """Produces deterministic prompts by injecting contexts, schemas, and constraints."""

    @staticmethod
    def build(
        template: str,
        context: str,
        constraints: list[str] | None = None,
        schema_instructions: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Interpolates variables and appends context, constraints, and schemas to the template."""
        try:
            kwargs["context"] = context
            formatted = template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter '{e.args[0]}' for prompt template.") from e
        except Exception as e:
            raise ValueError(f"Error formatting prompt template: {e}") from e

        final_prompt = f"{formatted}\n\n[OPERATIONAL CONTEXT]\n{context}"

        if constraints:
            constraint_block = "\n".join(f"- {c}" for c in constraints)
            final_prompt += f"\n\n[CONSTRAINTS]\n{constraint_block}"

        if schema_instructions:
            final_prompt += f"\n\n[SCHEMA INSTRUCTIONS]\n{schema_instructions}"

        return final_prompt
