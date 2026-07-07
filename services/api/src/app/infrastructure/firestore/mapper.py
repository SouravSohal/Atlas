from abc import ABC, abstractmethod
from typing import Any

from atlas_core.domain.entities.base import BaseEntity


class CollectionMapper[T: BaseEntity](ABC):
    """Abstract mapper for serializing and deserializing domain entities to/from Firestore documents."""

    @abstractmethod
    def to_document(self, entity: T) -> dict[str, Any]:
        """Serializes a domain entity into a document dictionary."""

    @abstractmethod
    def to_entity(self, document_id: str, data: dict[str, Any]) -> T:
        """Deserializes a document dictionary into a domain entity."""
