from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Protocol

from atlas_core.domain.entities.base import BaseEntity


class DocumentMapper[T: BaseEntity](Protocol):
    """Protocol for serializing/deserializing domain entities to/from dictionaries."""

    def to_document(self, entity: T) -> dict[str, Any]:
        """Serializes a domain entity into a document dictionary."""
        ...

    def to_entity(self, document_id: str, data: dict[str, Any]) -> T:
        """Deserializes a document dictionary into a domain entity."""
        ...


class CollectionMapper[T: BaseEntity](ABC):
    """Abstract mapper for serializing and deserializing domain entities to/from Firestore documents."""

    @abstractmethod
    def to_document(self, entity: T) -> dict[str, Any]:
        """Serializes a domain entity into a document dictionary."""

    @abstractmethod
    def to_entity(self, document_id: str, data: dict[str, Any]) -> T:
        """Deserializes a document dictionary into a domain entity."""


class TimestampMapper:
    """Helper to convert and normalize Python datetime and Firestore Timestamp objects."""

    @staticmethod
    def to_datetime(val: Any) -> datetime | None:
        """Converts raw Timestamp or string representation to a timezone-aware UTC datetime."""
        if val is None:
            return None
        if isinstance(val, datetime):
            if val.tzinfo is None:
                return val.replace(tzinfo=UTC)
            return val.astimezone(UTC)
        if hasattr(val, "to_datetime") and callable(val.to_datetime):
            return val.to_datetime().replace(tzinfo=UTC)  # type: ignore[no-any-return]
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00")).astimezone(UTC)
            except ValueError:
                pass
        return None

    @staticmethod
    def to_timestamp(val: datetime | None) -> datetime | None:
        """Normalizes a Python datetime object to timezone-aware UTC datetime for Firestore."""
        if val is None:
            return None
        if val.tzinfo is None:
            return val.replace(tzinfo=UTC)
        return val.astimezone(UTC)
