from typing import Any


class PromptBuilder:
    """Helper to build prompt content with context and formatting."""

    @staticmethod
    def build(template: str, **kwargs: Any) -> str:
        """Interpolates variables into the prompt template."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter '{e.args[0]}' for prompt template.") from e
        except IndexError as e:
            raise ValueError(f"Invalid placeholder in prompt template: {e}") from e
        except ValueError as e:
            raise ValueError(f"Error formatting prompt template: {e}") from e
        except Exception as e:
            raise ValueError(f"Unexpected formatting error in template: {e}") from e
