from datetime import UTC, datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.task import Task
from atlas_core.domain.exceptions.validation_error import ValidationException


def test_task_creation_valid() -> None:
    # Arrange & Act
    task = Task(title="Clean Gate 4", description="Spill clean up")

    # Assert
    assert task.title == "Clean Gate 4"
    assert task.description == "Spill clean up"
    assert task.assigned_to_id is None
    assert not task.completed

def test_task_creation_empty_title() -> None:
    # Act & Assert
    with pytest.raises(ValidationException, match="Task title cannot be empty"):
        Task(title="  ", description="description")

def test_task_creation_invalid_completed_at_timezone() -> None:
    # Act & Assert
    with pytest.raises(ValidationException, match="Task completed_at must be timezone-aware UTC"):
        Task(
            title="Clean Gate 4",
            description="description",
            completed=True,
            completed_at=datetime.now(),
        )

def test_task_creation_completed_at_without_completed() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationException, match="Task completed_at cannot be set if task is not completed"
    ):
        Task(
            title="Clean Gate 4",
            description="description",
            completed=False,
            completed_at=datetime.now(UTC),
        )

def test_task_assign_and_complete() -> None:
    # Arrange
    task = Task(title="Clean Gate 4", description="Spill clean up")
    user_id = uuid4()

    # Act
    task.assign_to(user_id)

    # Assert
    assert task.assigned_to_id == user_id

    # Act
    task.complete()

    # Assert
    assert task.completed
    assert task.completed_at is not None
    assert task.completed_at.tzinfo == UTC
