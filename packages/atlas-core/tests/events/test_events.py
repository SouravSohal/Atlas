from datetime import datetime
from uuid import uuid4

import pytest

from atlas_core.domain.events.base import DomainEvent
from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity


def test_domain_event_defaults() -> None:
    # Arrange
    agg_id = uuid4()

    # Act
    event = DomainEvent(aggregate_id=agg_id)

    # Assert
    assert event.aggregate_id == agg_id
    assert event.event_id is not None
    assert event.occurred_at is not None
    assert event.event_type == "DomainEvent"

def test_domain_event_invalid_timezone() -> None:
    # Act & Assert
    with pytest.raises(ValueError, match="occurred_at must be a timezone-aware UTC datetime"):
        DomainEvent(aggregate_id=uuid4(), occurred_at=datetime.now())

def test_crowd_density_changed_event() -> None:
    # Arrange
    agg_id = uuid4()
    loc = Coordinates(latitude=0.0, longitude=0.0)
    prev = CrowdDensity(value=0.1)
    new = CrowdDensity(value=0.5)

    # Act
    event = CrowdDensityChanged(
        aggregate_id=agg_id, location=loc, previous_density=prev, new_density=new
    )

    # Assert
    assert event.event_type == "CrowdDensityChanged"
    assert event.location == loc
