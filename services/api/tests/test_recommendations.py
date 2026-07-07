
import pytest
from atlas_core.domain.enums.severity import Severity

from app.application.operational_state.exceptions import InvalidStateTransitionException
from app.application.recommendations import (
    RecommendationEngine,
    RecommendationEvaluator,
    RecommendationFactory,
    RecommendationPriorityCalculator,
    RecommendationValidator,
)


def test_recommendation_validator_invalid_params() -> None:
    # Arrange & Act & Assert
    with pytest.raises(InvalidStateTransitionException, match="Crowd density must be between"):
        RecommendationValidator.validate_generation_params(
            crowd_density=1.5,
            incident_severity=Severity.LOW,
            queue_length=10,
            volunteer_availability=5,
            stadium_capacity=50000,
        )

    with pytest.raises(InvalidStateTransitionException, match="Queue length cannot be negative"):
        RecommendationValidator.validate_generation_params(
            crowd_density=0.5,
            incident_severity=Severity.LOW,
            queue_length=-5,
            volunteer_availability=5,
            stadium_capacity=50000,
        )

    with pytest.raises(InvalidStateTransitionException, match="Volunteer availability cannot be negative"):
        RecommendationValidator.validate_generation_params(
            crowd_density=0.5,
            incident_severity=Severity.LOW,
            queue_length=10,
            volunteer_availability=-1,
            stadium_capacity=50000,
        )

    with pytest.raises(InvalidStateTransitionException, match="Stadium capacity must be positive"):
        RecommendationValidator.validate_generation_params(
            crowd_density=0.5,
            incident_severity=Severity.LOW,
            queue_length=10,
            volunteer_availability=5,
            stadium_capacity=0,
        )

    with pytest.raises(InvalidStateTransitionException, match="Invalid severity value"):
        RecommendationValidator.validate_generation_params(
            crowd_density=0.5,
            incident_severity="SUPER_CRITICAL",
            queue_length=10,
            volunteer_availability=5,
            stadium_capacity=10000,
        )


def test_recommendation_priority_calculator() -> None:
    # Arrange & Act & Assert
    # Critical cases
    assert RecommendationPriorityCalculator.calculate(0.5, Severity.CRITICAL, 10) == Severity.CRITICAL
    assert RecommendationPriorityCalculator.calculate(0.95, Severity.HIGH, 10) == Severity.CRITICAL
    assert RecommendationPriorityCalculator.calculate(0.5, Severity.LOW, 50) == Severity.CRITICAL

    # High cases
    assert RecommendationPriorityCalculator.calculate(0.5, Severity.HIGH, 10) == Severity.HIGH
    assert RecommendationPriorityCalculator.calculate(0.8, Severity.LOW, 10) == Severity.HIGH
    assert RecommendationPriorityCalculator.calculate(0.5, Severity.LOW, 35) == Severity.HIGH

    # Medium cases
    assert RecommendationPriorityCalculator.calculate(0.5, Severity.MEDIUM, 10) == Severity.MEDIUM
    assert RecommendationPriorityCalculator.calculate(0.6, Severity.LOW, 10) == Severity.MEDIUM
    assert RecommendationPriorityCalculator.calculate(0.5, Severity.LOW, 20) == Severity.MEDIUM

    # Low cases
    assert RecommendationPriorityCalculator.calculate(0.3, Severity.LOW, 5) == Severity.LOW


def test_recommendation_evaluator() -> None:
    # Arrange & Act
    results_halt = RecommendationEvaluator.evaluate(
        crowd_density=0.98,
        incident_severity=Severity.LOW,
        queue_length=5,
        volunteer_availability=0,
        stadium_capacity=50000,
    )
    # Assert Halt Entry
    assert any(r.action_type == "HALT_ENTRY" for r in results_halt)

    # Dispatch responders
    results_dispatch = RecommendationEvaluator.evaluate(
        crowd_density=0.2,
        incident_severity=Severity.CRITICAL,
        queue_length=5,
        volunteer_availability=0,
        stadium_capacity=50000,
    )
    assert any(r.action_type == "DISPATCH_RESPONDERS" for r in results_dispatch)

    # Reroute Crowd
    results_reroute = RecommendationEvaluator.evaluate(
        crowd_density=0.82,
        incident_severity=Severity.LOW,
        queue_length=5,
        volunteer_availability=0,
        stadium_capacity=50000,
    )
    assert any(r.action_type == "REROUTE_CROWD" for r in results_reroute)

    # Open gates
    results_gates = RecommendationEvaluator.evaluate(
        crowd_density=0.5,
        incident_severity=Severity.LOW,
        queue_length=30,
        volunteer_availability=0,
        stadium_capacity=50000,
    )
    assert any(r.action_type == "OPEN_GATES" for r in results_gates)

    # Allocate volunteers
    results_vols = RecommendationEvaluator.evaluate(
        crowd_density=0.5,
        incident_severity=Severity.LOW,
        queue_length=18,
        volunteer_availability=4,
        stadium_capacity=50000,
    )
    assert any(r.action_type == "ALLOCATE_VOLUNTEERS" for r in results_vols)


def test_recommendation_factory() -> None:
    # Arrange & Act
    rec = RecommendationFactory.create(
        action_type="REROUTE_CROWD",
        priority=Severity.HIGH,
        confidence_value=0.9,
        details="Reroute description",
    )

    # Assert
    assert rec.action_type == "REROUTE_CROWD"
    assert rec.priority == Severity.HIGH
    assert rec.confidence.value == 0.9
    assert rec.details == "Reroute description"


def test_recommendation_engine_generate() -> None:
    # Arrange
    engine = RecommendationEngine()

    # Act
    recommendations = engine.generate(
        crowd_density=0.85,
        incident_severity=Severity.HIGH,
        queue_length=30,
        volunteer_availability=5,
        stadium_capacity=45000,
    )

    # Assert
    assert len(recommendations) > 0
    # Priority calculations should lead to HIGH or CRITICAL
    for rec in recommendations:
        assert rec.priority in (Severity.HIGH, Severity.CRITICAL)
        assert rec.confidence.value > 0.0
        assert len(rec.details) > 0
