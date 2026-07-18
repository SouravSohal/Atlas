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

from collections.abc import Sequence

from google.cloud import firestore


class FirestoreIncidentRepository(BaseRepository[Incident], IncidentRepository[Incident]):
    """Firestore implementation of the IncidentRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "incidents", IncidentMapper())

    async def list_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        resolved: bool | None = None,
        severity: str | None = None,
        incident_type: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[Sequence[Incident], int]:
        """Retrieves a paginated, filtered, and sorted list of incidents and the total count directly from Firestore."""
        # Initialize query by applying sorting first so the type is AsyncQuery from the start
        direction = firestore.Query.DESCENDING if order == "desc" else firestore.Query.ASCENDING
        query = self.collection_ref.order_by(sort_by, direction=direction)

        # Apply filters in Firestore
        if resolved is not None:
            query = query.where("resolved", "==", resolved)
        if severity is not None:
            query = query.where("severity", "==", severity)
        if incident_type is not None:
            query = query.where("incident_type", "==", incident_type)

        # Get total count via aggregation query (extremely lightweight/performant)
        count_query = query.count()
        get_method = getattr(count_query, "get")
        count_result = await get_method()
        total_count = int(count_result[0][0].value)

        # Apply pagination limit and offset in Firestore
        start = (page - 1) * limit
        query = query.offset(start).limit(limit)

        # Stream documents from Firestore
        results = []
        async for doc in query.stream():
            data = doc.to_dict()
            if data is not None:
                results.append(self.mapper.to_entity(doc.id, data))

        return results, total_count
