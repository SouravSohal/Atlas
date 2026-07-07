import logging
from collections.abc import Awaitable, Callable
from typing import Any, cast

import structlog
from google.api_core.exceptions import Aborted, ResourceExhausted, ServiceUnavailable
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger()

class RetryStrategy:
    """Manages automatic retry logic with exponential backoff for transient Firestore operations."""

    @staticmethod
    def get_retry_decorator(
        max_attempts: int = 3,
        min_seconds: float = 1.0,
        max_seconds: float = 10.0,
    ) -> Any:
        """Returns a tenacity retry decorator configured for transient GCP/Firestore errors."""
        return retry(
            reraise=True,
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
            retry=retry_if_exception_type((Aborted, ResourceExhausted, ServiceUnavailable)),
            before_sleep=before_sleep_log(logger, logging.DEBUG),
        )

    @staticmethod
    async def execute[R](
        func: Callable[[], Awaitable[R]],
        max_attempts: int = 3,
        min_seconds: float = 1.0,
        max_seconds: float = 10.0,
    ) -> R:
        """Executes an async callable with automatic retry logic."""
        decorator = RetryStrategy.get_retry_decorator(
            max_attempts=max_attempts,
            min_seconds=min_seconds,
            max_seconds=max_seconds,
        )
        res = await decorator(func)()
        return cast(R, res)
