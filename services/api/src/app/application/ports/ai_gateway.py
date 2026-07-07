from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AiGateway(ABC):
    """Abstract interface for interaction with Generative AI / Large Language Models.

    Purpose:
        Abstract generative model invocation, schema enforcement, and parameter layout.

    Responsibilities:
        - Invoke LLMs with dynamic prompt variables.
        - Parse and validate output against Pydantic models.

    Lifecycle:
        Singleton.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        - ValueError: If prompt parameters or schema validation fails.
        - ConnectionError: If connection to AI model endpoints fails.
    """

    @abstractmethod
    async def generate[T: BaseModel](
        self,
        prompt_name: str,
        context: Any,
        schema: type[T],
        **prompt_vars: Any,
    ) -> T:
        """Generates a structured Pydantic response using AI."""

    @abstractmethod
    async def generate_text(
        self,
        prompt_name: str,
        context: Any,
        **prompt_vars: Any,
    ) -> str:
        """Generates raw string response using AI."""
