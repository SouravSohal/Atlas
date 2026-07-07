from typing import Any
from uuid import UUID

from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.value_objects.coordinates import Coordinates

from app.infrastructure.firestore import BaseRepository, CollectionMapper, FirestoreClient


class IncidentMapper(CollectionMapper[Incident]):
    """Mapper to serialize and deserialize Incident domain entities to/from Firestore."""

    def to_document(self, entity: Incident) -> dict[str, Any]:
        return {
            "id": str(entity.id),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "version": entity.version,
            "incident_type": entity.incident_type.value,
            "severity": entity.severity.value,
            "description": entity.description,
            "location": {
                "latitude": entity.location.latitude,
                "longitude": entity.location.longitude,
            },
            "reporter_id": str(entity.reporter_id),
            "resolved": entity.resolved,
            "resolved_at": entity.resolved_at,
        }

    def to_entity(self, document_id: str, data: dict[str, Any]) -> Incident:
        loc_data = data["location"]
        return Incident(
            id=UUID(document_id),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            incident_type=IncidentType(data["incident_type"]),
            severity=Severity(data["severity"]),
            description=data["description"],
            location=Coordinates(
                latitude=loc_data["latitude"],
                longitude=loc_data["longitude"],
            ),
            reporter_id=UUID(data["reporter_id"]),
            resolved=data["resolved"],
            resolved_at=data.get("resolved_at"),
        )

class FirestoreIncidentRepository(BaseRepository[Incident], IncidentRepository[Incident]):
    """Firestore implementation of the IncidentRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "incidents", IncidentMapper())
