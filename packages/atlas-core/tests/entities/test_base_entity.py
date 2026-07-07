from datetime import datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.events.base import DomainEvent


class SimpleEntity(BaseEntity):
    pass

class SimpleEvent(DomainEvent):
    pass

def test_base_entity_initialization() -> None:
    # Arrange & Act
    entity = SimpleEntity()

    # Assert
    assert entity.id is not None
    assert entity.created_at is not None
    assert entity.updated_at is not None
    assert entity.version == 1
    assert len(entity.domain_events) == 0

def test_base_entity_equality_and_hashing() -> None:
    # Arrange
    entity_id = uuid4()
    entity1 = SimpleEntity(id=entity_id)
    entity2 = SimpleEntity(id=entity_id)
    entity3 = SimpleEntity()

    # Assert
    assert entity1 == entity2
    assert entity1 != entity3
    assert entity1 != "not_an_entity"
    assert hash(entity1) == hash(entity2)
    assert hash(entity1) != hash(entity3)

def test_base_entity_invalid_timezone() -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="created_at must be a timezone-aware UTC datetime"):
        SimpleEntity(created_at=datetime.now())

    with pytest.raises(ValueError, match="updated_at must be a timezone-aware UTC datetime"):
        SimpleEntity(updated_at=datetime.now())

def test_base_entity_event_recording() -> None:
    # Arrange
    entity = SimpleEntity()
    event = SimpleEvent(aggregate_id=entity.id)

    # Act
    entity.record_event(event)

    # Assert
    assert len(entity.domain_events) == 1
    assert entity.domain_events[0] == event

    # Act
    entity.clear_events()

    # Assert
    assert len(entity.domain_events) == 0
