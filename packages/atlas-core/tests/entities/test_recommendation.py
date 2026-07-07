from datetime import datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.exceptions.validation_error import ValidationException
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore


def test_recommendation_flow() -> None:
    # Arrange
    confidence = ConfidenceScore(value=0.95)
    rec = Recommendation(
        action_type="reroute",
        priority=Severity.HIGH,
        confidence=confidence,
        details="Reroute crowd from Gate A to Gate B",
        status=RecommendationStatus.PENDING,
    )

    # Assert Initial
    initial_status: RecommendationStatus = rec.status
    assert initial_status == RecommendationStatus.PENDING
    assert len(rec.domain_events) == 1

    # Act: Approve
    operator_id = uuid4()
    rec.approve(operator_id)

    # Assert Approved
    approved_status: RecommendationStatus = rec.status
    assert approved_status == RecommendationStatus.APPROVED
    assert rec.approved_by_id == operator_id
    assert rec.approved_at is not None
    assert len(rec.domain_events) == 2

    # Act: Execute
    rec.execute()
    executing_status: RecommendationStatus = rec.status
    assert executing_status == RecommendationStatus.EXECUTING

    # Act: Complete
    rec.complete()
    completed_status: RecommendationStatus = rec.status
    assert completed_status == RecommendationStatus.COMPLETED

def test_recommendation_reject_or_fail() -> None:
    # Arrange
    rec = Recommendation(
        action_type="reroute",
        priority=Severity.LOW,
        confidence=ConfidenceScore(value=0.8),
        details="Close gate early",
        status=RecommendationStatus.PENDING,
    )

    # Act & Assert Reject
    rec.reject()
    rejected_status: RecommendationStatus = rec.status
    assert rejected_status == RecommendationStatus.REJECTED

    # Arrange new
    rec2 = Recommendation(
        action_type="reroute",
        priority=Severity.LOW,
        confidence=ConfidenceScore(value=0.8),
        details="Close gate early",
        status=RecommendationStatus.PENDING,
    )
    rec2.fail()
    failed_status: RecommendationStatus = rec2.status
    assert failed_status == RecommendationStatus.FAILED

def test_recommendation_creation_empty_action_type() -> None:
    # Act & Assert
    with pytest.raises(ValidationException, match="Recommendation action_type cannot be empty"):
        Recommendation(
            action_type="  ",
            priority=Severity.LOW,
            confidence=ConfidenceScore(value=0.8),
            details="details",
        )

def test_recommendation_creation_empty_details() -> None:
    # Act & Assert
    with pytest.raises(ValidationException, match="Recommendation details cannot be empty"):
        Recommendation(
            action_type="reroute",
            priority=Severity.LOW,
            confidence=ConfidenceScore(value=0.8),
            details="  ",
        )

def test_recommendation_creation_approved_without_operator_or_time() -> None:
    # Act & Assert
    with pytest.raises(
        ValidationException,
        match="Approved recommendations must have approved_by_id and approved_at set",
    ):
        Recommendation(
            action_type="reroute",
            priority=Severity.LOW,
            confidence=ConfidenceScore(value=0.8),
            details="details",
            status=RecommendationStatus.APPROVED,
        )

def test_recommendation_creation_invalid_approved_at_timezone() -> None:
    # Act & Assert
    with pytest.raises(ValidationException, match="Recommendation approved_at must be timezone-aware UTC"):
        Recommendation(
            action_type="reroute",
            priority=Severity.LOW,
            confidence=ConfidenceScore(value=0.8),
            details="details",
            status=RecommendationStatus.APPROVED,
            approved_by_id=uuid4(),
            approved_at=datetime.now(),
        )

def test_recommendation_invalid_transitions() -> None:
    # Arrange
    rec = Recommendation(
        action_type="reroute",
        priority=Severity.LOW,
        confidence=ConfidenceScore(value=0.8),
        details="details",
        status=RecommendationStatus.PENDING,
    )

    # Act & Assert
    with pytest.raises(ValidationException, match="Only APPROVED recommendations can be executed"):
        rec.execute()

    with pytest.raises(ValidationException, match="Only EXECUTING recommendations can be marked completed"):
        rec.complete()

    rec.approve(uuid4())
    with pytest.raises(ValidationException, match="Only PENDING recommendations can be approved"):
        rec.approve(uuid4())

    with pytest.raises(ValidationException, match="Only PENDING recommendations can be rejected"):
        rec.reject()

    rec.execute()
    rec.complete()
    with pytest.raises(ValidationException, match="Terminal recommendations cannot be marked failed"):
        rec.fail()
