from datetime import UTC, datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.coordinates import Coordinates


def test_incident_creation_valid() -> None:
    # Arrange
    coords = Coordinates(latitude=12.34, longitude=56.78)
    reporter = uuid4()

    # Act
    incident = Incident(
        incident_type=IncidentType.MEDICAL,
        severity=Severity.HIGH,
        description="Fainting fan in block C",
        location=coords,
        reporter_id=reporter,
    )

    # Assert
    assert incident.incident_type == IncidentType.MEDICAL
    assert incident.severity == Severity.HIGH
    assert incident.description == "Fainting fan in block C"
    assert incident.location == coords
    assert incident.reporter_id == reporter
    assert not incident.resolved
    assert incident.resolved_at is None
    assert len(incident.domain_events) == 1

def test_incident_creation_empty_description() -> None:
    # Arrange
    coords = Coordinates(latitude=12.34, longitude=56.78)
    # Act & Assert
    with pytest.raises(ValidationException, match="Incident description cannot be empty"):
        Incident(
            incident_type=IncidentType.MEDICAL,
            severity=Severity.HIGH,
            description="  ",
            location=coords,
            reporter_id=uuid4(),
        )

def test_incident_creation_invalid_resolved_at_timezone() -> None:
    # Arrange
    coords = Coordinates(latitude=12.34, longitude=56.78)
    # Act & Assert
    with pytest.raises(ValidationException, match="Incident resolved_at must be timezone-aware UTC"):
        Incident(
            incident_type=IncidentType.MEDICAL,
            severity=Severity.HIGH,
            description="Fainting fan",
            location=coords,
            reporter_id=uuid4(),
            resolved=True,
            resolved_at=datetime.now(),
        )

def test_incident_creation_resolved_at_without_resolved() -> None:
    # Arrange
    coords = Coordinates(latitude=12.34, longitude=56.78)
    # Act & Assert
    with pytest.raises(
        ValidationException, match="Incident resolved_at cannot be set if incident is not resolved"
    ):
        Incident(
            incident_type=IncidentType.MEDICAL,
            severity=Severity.HIGH,
            description="Fainting fan",
            location=coords,
            reporter_id=uuid4(),
            resolved=False,
            resolved_at=datetime.now(UTC),
        )

def test_incident_resolve() -> None:
    # Arrange
    coords = Coordinates(latitude=12.34, longitude=56.78)
    incident = Incident(
        incident_type=IncidentType.SECURITY,
        severity=Severity.CRITICAL,
        description="Fight at Gate 2",
        location=coords,
        reporter_id=uuid4(),
    )

    # Act
    incident.resolve()

    # Assert
    assert incident.resolved
    assert incident.resolved_at is not None
    assert incident.resolved_at.tzinfo == UTC

def test_incident_update_severity() -> None:
    # Arrange
    coords = Coordinates(latitude=12.34, longitude=56.78)
    incident = Incident(
        incident_type=IncidentType.FACILITY,
        severity=Severity.LOW,
        description="Broken seat 42B",
        location=coords,
        reporter_id=uuid4(),
    )

    # Act
    incident.update_severity(Severity.MEDIUM)

    # Assert
    assert incident.severity == Severity.MEDIUM
