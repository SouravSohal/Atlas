from typing import Any
from uuid import UUID

from atlas_core.domain.entities.event import Event
from atlas_core.domain.enums.event_type import EventType
from atlas_core.domain.repositories.event_repository import EventRepository

from app.infrastructure.firestore import BaseRepository, CollectionMapper, FirestoreClient


class EventMapper(CollectionMapper[Event]):
    """Mapper to serialize and deserialize Event domain entities to/from Firestore."""

    def to_document(self, entity: Event) -> dict[str, Any]:
        return {
            "id": str(entity.id),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "version": entity.version,
            "name": entity.name,
            "event_type": entity.event_type.value,
            "start_time": entity.start_time,
            "end_time": entity.end_time,
        }

    def to_entity(self, document_id: str, data: dict[str, Any]) -> Event:
        return Event(
            id=UUID(document_id),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            name=data["name"],
            event_type=EventType(data["event_type"]),
            start_time=data["start_time"],
            end_time=data.get("end_time"),
        )

class FirestoreEventRepository(BaseRepository[Event], EventRepository[Event]):
    """Firestore implementation of the EventRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "events", EventMapper())
