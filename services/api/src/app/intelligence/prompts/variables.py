from pydantic import BaseModel


class PromptVariables(BaseModel):
    """Base class for prompt interpolation variables, enabling strict validation."""

