from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.exceptions.validation_error import ValidationException


@dataclass(kw_only=True)
class Task(BaseEntity):
    """Represents a discrete action/assignment in the system."""

    title: str
    description: str
    assigned_to_id: UUID | None = None
    incident_id: UUID | None = None
    completed: bool = False
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.title.strip():
            raise ValidationException("Task title cannot be empty.")
        if self.completed_at is not None:
            if self.completed_at.tzinfo is None or self.completed_at.tzinfo != UTC:
                raise ValidationException("Task completed_at must be timezone-aware UTC.")
            if not self.completed:
                raise ValidationException("Task completed_at cannot be set if task is not completed.")

    def assign_to(self, user_id: UUID) -> None:
        """Assign the task to a specific user."""
        self.assigned_to_id = user_id
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True
        self.completed_at = datetime.now(UTC)
        self.updated_at = self.completed_at
