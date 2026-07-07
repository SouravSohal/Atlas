from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.enums.user_role import UserRole


def test_user_role_is_staff() -> None:
    # Assert
    assert UserRole.ADMIN.is_staff()
    assert UserRole.OPERATOR.is_staff()
    assert not UserRole.VOLUNTEER.is_staff()
    assert not UserRole.FAN.is_staff()
    assert not UserRole.ATHLETE.is_staff()

def test_incident_type_requires_dispatch() -> None:
    # Assert
    assert IncidentType.MEDICAL.requires_immediate_dispatch()
    assert IncidentType.SECURITY.requires_immediate_dispatch()
    assert IncidentType.CROWD_CONTROL.requires_immediate_dispatch()
    assert not IncidentType.FACILITY.requires_immediate_dispatch()
    assert not IncidentType.WEATHER.requires_immediate_dispatch()
    assert not IncidentType.OTHER.requires_immediate_dispatch()

def test_recommendation_status_is_terminal() -> None:
    # Assert
    assert RecommendationStatus.COMPLETED.is_terminal()
    assert RecommendationStatus.FAILED.is_terminal()
    assert RecommendationStatus.REJECTED.is_terminal()
    assert not RecommendationStatus.PENDING.is_terminal()
    assert not RecommendationStatus.APPROVED.is_terminal()
    assert not RecommendationStatus.EXECUTING.is_terminal()

def test_severity_properties() -> None:
    # Assert level
    assert Severity.INFO.level == 0
    assert Severity.LOW.level == 1
    assert Severity.MEDIUM.level == 2
    assert Severity.HIGH.level == 3
    assert Severity.CRITICAL.level == 4

    # Assert is_urgent
    assert not Severity.INFO.is_urgent()
    assert not Severity.LOW.is_urgent()
    assert not Severity.MEDIUM.is_urgent()
    assert Severity.HIGH.is_urgent()
    assert Severity.CRITICAL.is_urgent()
