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

from collections.abc import Sequence

from google.cloud import firestore


class FirestoreRecommendationRepository(BaseRepository[Recommendation], RecommendationRepository[Recommendation]):
    """Firestore implementation of the RecommendationRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "recommendations", RecommendationMapper())

    async def list_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        status: str | None = None,
        priority: str | None = None,
        action_type: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[Sequence[Recommendation], int]:
        """Retrieves a paginated, filtered, and sorted list of recommendations and total count directly from Firestore."""
        # Initialize query by applying sorting first so the type is AsyncQuery from the start
        direction = firestore.Query.DESCENDING if order == "desc" else firestore.Query.ASCENDING
        query = self.collection_ref.order_by(sort_by, direction=direction)

        # Apply filters in Firestore
        if status is not None:
            query = query.where("status", "==", status)
        if priority is not None:
            query = query.where("priority", "==", priority)
        if action_type is not None:
            query = query.where("action_type", "==", action_type)

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
