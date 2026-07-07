from abc import ABC, abstractmethod


class TranslationGateway(ABC):
    """Abstract interface for translating text between languages.

    Purpose:
        Provide translation capabilities to localize messages or operational text.

    Responsibilities:
        - Translate text from a source language to a target language.

    Lifecycle:
        Singleton.

    Thread Safety:
        Must be thread-safe.

    Error Expectations:
        - ValueError: If inputs are invalid.
        - ConnectionError: If connection to external translation service fails.
    """

    @abstractmethod
    async def translate(self, text: str, target_language: str, source_language: str | None = None) -> str:
        """Translates text to target language."""
