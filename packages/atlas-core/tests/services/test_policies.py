from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.services.crowd_policy import CrowdPolicy
from atlas_core.domain.services.incident_policy import IncidentPolicy
from atlas_core.domain.services.navigation_policy import NavigationPolicy
from atlas_core.domain.services.recommendation_policy import RecommendationPolicy
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


def test_crowd_policy() -> None:
    # Arrange
    low_density = CrowdDensity(value=0.2)
    medium_density_1 = CrowdDensity(value=0.45)
    medium_density_2 = CrowdDensity(value=0.72)
    high_density = CrowdDensity(value=0.85)
    short_queue = QueueEstimate(waiting_minutes=5)
    long_queue = QueueEstimate(waiting_minutes=20)

    # Assert
    assert not CrowdPolicy.is_overcrowded(low_density)
    assert CrowdPolicy.is_overcrowded(high_density)
    assert CrowdPolicy.should_trigger_rerouting(medium_density_2, long_queue)
    assert not CrowdPolicy.should_trigger_rerouting(medium_density_2, short_queue)

    assert CrowdPolicy.determine_required_staff_count(low_density) == 2
    assert CrowdPolicy.determine_required_staff_count(medium_density_1) == 5
    assert CrowdPolicy.determine_required_staff_count(medium_density_2) == 10
    assert CrowdPolicy.determine_required_staff_count(high_density) == 20

def test_recommendation_policy() -> None:
    # Arrange
    high_conf = ConfidenceScore(value=0.95)
    low_conf = ConfidenceScore(value=0.85)

    # Assert
    assert RecommendationPolicy.should_auto_approve(Severity.HIGH, high_conf)
    assert not RecommendationPolicy.should_auto_approve(Severity.CRITICAL, high_conf)
    assert not RecommendationPolicy.should_auto_approve(Severity.HIGH, low_conf)
    assert RecommendationPolicy.is_valid_transition(
        RecommendationStatus.PENDING, RecommendationStatus.APPROVED
    )
    assert not RecommendationPolicy.is_valid_transition(
        RecommendationStatus.REJECTED, RecommendationStatus.APPROVED
    )

def test_navigation_policy() -> None:
    # Arrange
    safe_densities = [CrowdDensity(value=0.1), CrowdDensity(value=0.5)]
    unsafe_densities = [CrowdDensity(value=0.1), CrowdDensity(value=0.92)]

    # Assert
    assert NavigationPolicy.is_route_safe(safe_densities)
    assert not NavigationPolicy.is_route_safe(unsafe_densities)
    assert NavigationPolicy.calculate_route_penalty(100.0, CrowdDensity(value=0.5)) == 200.0

def test_incident_policy() -> None:
    # Assert
    assert (
        IncidentPolicy.determine_dispatch_urgency(IncidentType.MEDICAL, Severity.LOW)
        == Severity.CRITICAL
    )
    assert (
        IncidentPolicy.determine_dispatch_urgency(IncidentType.SECURITY, Severity.CRITICAL)
        == Severity.CRITICAL
    )
    assert (
        IncidentPolicy.determine_dispatch_urgency(IncidentType.SECURITY, Severity.HIGH)
        == Severity.CRITICAL
    )
    assert (
        IncidentPolicy.determine_dispatch_urgency(IncidentType.SECURITY, Severity.LOW)
        == Severity.LOW
    )
    assert (
        IncidentPolicy.determine_dispatch_urgency(IncidentType.FACILITY, Severity.CRITICAL)
        == Severity.CRITICAL
    )
    assert (
        IncidentPolicy.determine_dispatch_urgency(IncidentType.FACILITY, Severity.LOW)
        == Severity.LOW
    )
    assert IncidentPolicy.requires_police_escalation(IncidentType.SECURITY, Severity.HIGH)
    assert not IncidentPolicy.requires_police_escalation(IncidentType.SECURITY, Severity.LOW)
    assert not IncidentPolicy.requires_police_escalation(IncidentType.FACILITY, Severity.CRITICAL)

