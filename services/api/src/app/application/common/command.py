from abc import ABC, abstractmethod

from app.application.common.result import Result


class Command:
    """Marker interface/base class for all Commands in the system."""

class CommandHandler[C: Command, R](ABC):
    """Interface for command handlers executing application operations."""

    @abstractmethod
    async def handle(self, command: C) -> Result[R]:
        """Handles the command and returns a Result."""
