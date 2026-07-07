from datetime import UTC, datetime, timedelta

import pytest

from atlas_core.domain.entities.event import Event
from atlas_core.domain.enums.event_type import EventType
from atlas_core.domain.exceptions.validation_error import ValidationException


def test_event_creation_valid() -> None:
    # Arrange
    start = datetime.now(UTC)

    # Act
    event = Event(name="Match 1", event_type=EventType.MATCH_STARTED, start_time=start)

    # Assert
    assert event.name == "Match 1"
    assert event.event_type == EventType.MATCH_STARTED
    assert event.start_time == start
    assert event.end_time is None

def test_event_creation_invalid_name() -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValidationException, match="Event name cannot be empty"):
        Event(name="", event_type=EventType.MATCH_STARTED, start_time=datetime.now(UTC))

def test_event_creation_invalid_timezone() -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValidationException, match="Event start_time must be timezone-aware UTC"):
        Event(name="Match 1", event_type=EventType.MATCH_STARTED, start_time=datetime.now())

def test_event_creation_invalid_end_time_timezone() -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValidationException, match="Event end_time must be timezone-aware UTC"):
        Event(
            name="Match 1",
            event_type=EventType.MATCH_STARTED,
            start_time=datetime.now(UTC),
            end_time=datetime.now(),
        )

def test_event_creation_invalid_end_time_before_start() -> None:
    # Arrange
    start = datetime.now(UTC)
    # Act & Assert
    with pytest.raises(ValidationException, match="Event end_time cannot be before start_time"):
        Event(
            name="Match 1",
            event_type=EventType.MATCH_STARTED,
            start_time=start,
            end_time=start - timedelta(hours=1),
        )

def test_event_completion_valid() -> None:
    # Arrange
    start = datetime.now(UTC)
    event = Event(name="Match 1", event_type=EventType.MATCH_STARTED, start_time=start)
    end = start + timedelta(hours=2)

    # Act
    event.complete(end)

    # Assert
    assert event.end_time == end

def test_event_completion_invalid_end_time_timezone() -> None:
    # Arrange
    start = datetime.now(UTC)
    event = Event(name="Match 1", event_type=EventType.MATCH_STARTED, start_time=start)

    # Act & Assert
    with pytest.raises(ValidationException, match="Event end_time must be timezone-aware UTC"):
        event.complete(datetime.now())

def test_event_completion_invalid_end_time() -> None:
    # Arrange
    start = datetime.now(UTC)
    event = Event(name="Match 1", event_type=EventType.MATCH_STARTED, start_time=start)

    # Act & Assert
    with pytest.raises(ValidationException, match="Event end_time cannot be before start_time"):
        event.complete(start - timedelta(hours=1))
