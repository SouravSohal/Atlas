from abc import ABC, abstractmethod

from app.application.common.result import Result


class Query:
    """Marker interface/base class for all Queries in the system."""

class QueryHandler[Q: Query, R](ABC):
    """Interface for query handlers executing application read operations."""

    @abstractmethod
    async def handle(self, query: Q) -> Result[R]:
        """Handles the query and returns a Result."""
