from typing import Any


class PromptTemplate:
    """Represents a compileable prompt template containing the raw text structure."""

    def __init__(self, content: str) -> None:
        self.content = content

    def render(self, **kwargs: Any) -> str:
        """Renders the raw template content with the provided variables."""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter '{e.args[0]}' for prompt template rendering.") from e
        except Exception as e:
            raise ValueError(f"Failed to render prompt template: {e}") from e
        return ""
