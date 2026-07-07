from datetime import UTC, datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


def test_operational_state_updates() -> None:
    # Arrange
    zone = uuid4()
    density1 = CrowdDensity(value=0.4)
    density2 = CrowdDensity(value=0.7)
    queue = QueueEstimate(waiting_minutes=5)
    coords = Coordinates(latitude=1.0, longitude=2.0)

    # Act
    state = OperationalState(
        zone_id=zone,
        density=density1,
        queue_estimate=queue,
        last_updated=datetime.now(UTC),
    )

    # Assert
    assert state.zone_id == zone
    assert state.density == density1
    assert len(state.domain_events) == 0

    # Act: update (same density, no event)
    state.update_state(density1, QueueEstimate(waiting_minutes=10), coords)
    assert len(state.domain_events) == 0

    # Act: update density (triggers event)
    state.update_state(density2, queue, coords)
    assert len(state.domain_events) == 1
    event = state.domain_events[0]
    from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
    assert isinstance(event, CrowdDensityChanged)
    assert event.aggregate_id == zone
    assert event.previous_density == density1
    assert event.new_density == density2
    assert event.location == coords

def test_operational_state_creation_invalid_timezone() -> None:
    # Arrange
    zone = uuid4()
    density = CrowdDensity(value=0.4)
    queue = QueueEstimate(waiting_minutes=5)

    # Act & Assert
    with pytest.raises(ValidationException, match="OperationalState last_updated must be timezone-aware UTC"):
        OperationalState(
            zone_id=zone,
            density=density,
            queue_estimate=queue,
            last_updated=datetime.now(),
        )
