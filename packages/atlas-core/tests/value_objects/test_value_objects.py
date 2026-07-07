import pytest

from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


def test_coordinates() -> None:
    # Arrange & Act
    coords = Coordinates(latitude=45.5, longitude=-122.5)

    # Assert
    assert coords.latitude == 45.5
    assert coords.longitude == -122.5
    assert str(coords) == "(45.500000, -122.500000)"
    assert repr(coords) == "Coordinates(latitude=45.5, longitude=-122.5)"

    with pytest.raises(ValidationException, match="Latitude must be between -90 and 90"):
        Coordinates(latitude=95.0, longitude=0.0)

    with pytest.raises(ValidationException, match="Latitude must be between -90 and 90"):
        Coordinates(latitude=-91.0, longitude=0.0)

    with pytest.raises(ValidationException, match="Longitude must be between -180 and 180"):
        Coordinates(latitude=0.0, longitude=185.0)

    with pytest.raises(ValidationException, match="Longitude must be between -180 and 180"):
        Coordinates(latitude=0.0, longitude=-181.0)

def test_crowd_density() -> None:
    # Arrange & Act
    d1 = CrowdDensity(value=0.25)
    d2 = CrowdDensity(value=0.5)

    # Assert
    assert d1.value == 0.25
    assert str(d1) == "25.0%"
    assert repr(d1) == "CrowdDensity(value=0.25)"
    assert d1 < d2
    assert d2 > d1

    # Casting
    d_cast = CrowdDensity(value="0.75")  # type: ignore
    assert d_cast.value == 0.75

    with pytest.raises(ValidationException, match="CrowdDensity value must be a float"):
        CrowdDensity(value="invalid")  # type: ignore

    with pytest.raises(ValidationException, match=r"CrowdDensity value must be between 0\.0 and 1\.0"):
        CrowdDensity(value=1.5)

    with pytest.raises(ValidationException, match=r"CrowdDensity value must be between 0\.0 and 1\.0"):
        CrowdDensity(value=-0.1)

    # Compare with invalid type
    with pytest.raises(TypeError):
        _ = d1 < 5

def test_queue_estimate() -> None:
    # Arrange & Act
    q1 = QueueEstimate(waiting_minutes=10)
    q2 = QueueEstimate(waiting_minutes=20)

    # Assert
    assert q1.waiting_minutes == 10
    assert str(q1) == "10 min"
    assert repr(q1) == "QueueEstimate(waiting_minutes=10)"
    assert q1 < q2

    with pytest.raises(ValidationException, match="QueueEstimate waiting minutes must be non-negative"):
        QueueEstimate(waiting_minutes=-5)

    # Compare with invalid type
    with pytest.raises(TypeError):
        _ = q1 < 5

def test_confidence_score() -> None:
    # Arrange & Act
    c1 = ConfidenceScore(value=0.85)
    c2 = ConfidenceScore(value=0.9)

    # Assert
    assert c1.value == 0.85
    assert str(c1) == "0.85"
    assert repr(c1) == "ConfidenceScore(value=0.85)"
    assert c1 < c2

    # Casting
    c_cast = ConfidenceScore(value="0.95")  # type: ignore
    assert c_cast.value == 0.95

    with pytest.raises(ValidationException, match="ConfidenceScore value must be a float"):
        ConfidenceScore(value="invalid")  # type: ignore

    with pytest.raises(ValidationException, match=r"ConfidenceScore value must be between 0\.0 and 1\.0"):
        ConfidenceScore(value=1.1)

    with pytest.raises(ValidationException, match=r"ConfidenceScore value must be between 0\.0 and 1\.0"):
        ConfidenceScore(value=-0.1)

    # Compare with invalid type
    with pytest.raises(TypeError):
        _ = c1 < 5

