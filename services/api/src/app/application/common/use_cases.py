from abc import ABC, abstractmethod


class BaseUseCase[TRequest, TResponse](ABC):
    """Base class for all application Use Cases."""

    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse:
        """Executes the core use case business logic."""
