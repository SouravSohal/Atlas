from typing import Any

import structlog


class LoggingClient:
    """Wrapper client for the structured logger."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger()

    def get_logger(self) -> Any:
        """Returns the configured logger instance."""
        return self._logger
