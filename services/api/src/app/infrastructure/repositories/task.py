from typing import Any
from uuid import UUID

from atlas_core.domain.entities.task import Task
from atlas_core.domain.repositories.task_repository import TaskRepository

from app.infrastructure.firestore import BaseRepository, CollectionMapper, FirestoreClient


class TaskMapper(CollectionMapper[Task]):
    """Mapper to serialize and deserialize Task domain entities to/from Firestore."""

    def to_document(self, entity: Task) -> dict[str, Any]:
        return {
            "id": str(entity.id),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "version": entity.version,
            "title": entity.title,
            "description": entity.description,
            "assigned_to_id": str(entity.assigned_to_id) if entity.assigned_to_id else None,
            "incident_id": str(entity.incident_id) if entity.incident_id else None,
            "completed": entity.completed,
            "completed_at": entity.completed_at,
        }

    def to_entity(self, document_id: str, data: dict[str, Any]) -> Task:
        assigned = data.get("assigned_to_id")
        incident = data.get("incident_id")
        return Task(
            id=UUID(document_id),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            title=data["title"],
            description=data["description"],
            assigned_to_id=UUID(assigned) if assigned else None,
            incident_id=UUID(incident) if incident else None,
            completed=data["completed"],
            completed_at=data.get("completed_at"),
        )

class FirestoreTaskRepository(BaseRepository[Task], TaskRepository[Task]):
    """Firestore implementation of the TaskRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "tasks", TaskMapper())
