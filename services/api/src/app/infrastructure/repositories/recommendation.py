from typing import Any
from uuid import UUID

from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore

from app.infrastructure.firestore import BaseRepository, CollectionMapper, FirestoreClient


class RecommendationMapper(CollectionMapper[Recommendation]):
    """Mapper to serialize and deserialize Recommendation domain entities to/from Firestore."""

    def to_document(self, entity: Recommendation) -> dict[str, Any]:
        return {
            "id": str(entity.id),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "version": entity.version,
            "action_type": entity.action_type,
            "priority": entity.priority.value,
            "confidence": entity.confidence.value,
            "details": entity.details,
            "status": entity.status.value,
            "approved_by_id": str(entity.approved_by_id) if entity.approved_by_id else None,
            "approved_at": entity.approved_at,
        }

    def to_entity(self, document_id: str, data: dict[str, Any]) -> Recommendation:
        approved_by = data.get("approved_by_id")
        return Recommendation(
            id=UUID(document_id),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            action_type=data["action_type"],
            priority=Severity(data["priority"]),
            confidence=ConfidenceScore(value=data["confidence"]),
            details=data["details"],
            status=RecommendationStatus(data["status"]),
            approved_by_id=UUID(approved_by) if approved_by else None,
            approved_at=data.get("approved_at"),
        )

class FirestoreRecommendationRepository(BaseRepository[Recommendation], RecommendationRepository[Recommendation]):
    """Firestore implementation of the RecommendationRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "recommendations", RecommendationMapper())
