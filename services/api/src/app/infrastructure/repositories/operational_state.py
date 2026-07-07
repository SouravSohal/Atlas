from typing import Any
from uuid import UUID

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate

from app.infrastructure.firestore import BaseRepository, CollectionMapper, FirestoreClient


class OperationalStateMapper(CollectionMapper[OperationalState]):
    """Mapper to serialize and deserialize OperationalState domain entities to/from Firestore."""

    def to_document(self, entity: OperationalState) -> dict[str, Any]:
        return {
            "id": str(entity.id),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "version": entity.version,
            "zone_id": str(entity.zone_id),
            "density": entity.density.value,
            "queue_estimate": entity.queue_estimate.waiting_minutes,
            "last_updated": entity.last_updated,
        }

    def to_entity(self, document_id: str, data: dict[str, Any]) -> OperationalState:
        return OperationalState(
            id=UUID(document_id),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            zone_id=UUID(data["zone_id"]),
            density=CrowdDensity(value=data["density"]),
            queue_estimate=QueueEstimate(waiting_minutes=data["queue_estimate"]),
            last_updated=data["last_updated"],
        )

class FirestoreOperationalStateRepository(BaseRepository[OperationalState], OperationalStateRepository[OperationalState]):
    """Firestore implementation of the OperationalStateRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "operational_states", OperationalStateMapper())
