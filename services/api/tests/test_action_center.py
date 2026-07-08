import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate

from app.application.events import EventPublisher
from app.infrastructure.streaming.broadcast import BroadcastService
from app.application.action_center import (
    PendingDecision,
    AuditLog,
    PendingDecisionRepository,
    AuditLogRepository,
    AIActionCenterUseCase,
    DecisionApproved,
    DecisionRejected,
    DecisionExplanationRequested,
    DecisionSimulated,
    DecisionDelegated,
)

@pytest.mark.asyncio
async def test_action_center_use_cases() -> None:
    # 1. Initialize repositories & mocks
    decision_repo = PendingDecisionRepository()
    audit_repo = AuditLogRepository()
    state_repo = MagicMock(spec=OperationalStateRepository)
    event_publisher = MagicMock(spec=EventPublisher)
    event_publisher.publish_many = AsyncMock()
    broadcast_service = MagicMock(spec=BroadcastService)
    broadcast_service.broadcast_to_all = AsyncMock()

    # 2. Setup mock state
    mock_state = MagicMock(spec=OperationalState)
    mock_state.queue_estimate = QueueEstimate(waiting_minutes=10)
    mock_state.density = CrowdDensity(value=0.5)
    mock_state.update_state = MagicMock()
    state_repo.get_all = AsyncMock(return_value=[mock_state])
    state_repo.save = AsyncMock()

    # 3. Create a pending decision
    decision_id = uuid4()
    rec_id = uuid4()
    decision = PendingDecision(
        id=decision_id,
        recommendation_id=rec_id,
        priority="high",
        severity="medium",
        confidence=0.9,
        expected_impact="High",
        estimated_resolution_time="10m",
        required_resources=["medical"],
        human_approval_requirement=True,
        suggested_action="Deploy medical team",
        explanation="Distressed spectator in Sector A",
        status="pending",
    )
    await decision_repo.save(decision)

    # 4. Instantiate Use Case
    use_case = AIActionCenterUseCase(
        decision_repo=decision_repo,
        audit_repo=audit_repo,
        state_repo=state_repo,
        event_publisher=event_publisher,
        broadcast_service=broadcast_service
    )

    # Test pending list
    pending_list = await use_case.get_pending_decisions()
    assert len(pending_list) == 1
    assert pending_list[0].id == str(decision_id)

    # Test Approve
    resp = await use_case.approve_decision(decision_id, "operator-1")
    assert resp.status == "approved"
    
    # Assert Audit log saved
    audits = await audit_repo.get_by_decision_id(decision_id)
    assert len(audits) == 1
    assert audits[0].action == "approve"
    assert audits[0].operator_id == "operator-1"

    # Assert Event published
    event_publisher.publish_many.assert_called_once()
    published_events = event_publisher.publish_many.call_args[0][0]
    assert isinstance(published_events[0], DecisionApproved)

    # Assert Operational State updated
    state_repo.get_all.assert_called_once()
    state_repo.save.assert_called_once_with(mock_state)

    # Assert Broadcast sent
    broadcast_service.broadcast_to_all.assert_called_once()

    # Test Reject
    event_publisher.publish_many.reset_mock()
    broadcast_service.broadcast_to_all.reset_mock()
    
    resp_reject = await use_case.reject_decision(decision_id, "operator-1", "Invalid resources")
    assert resp_reject.status == "rejected"
    assert resp_reject.operator_notes == "Invalid resources"
    
    # Assert simulated
    resp_sim = await use_case.simulate_decision(decision_id, "operator-1", {"speed": 2})
    assert resp_sim.status == "simulated"

    # Assert delegated
    resp_del = await use_case.delegate_decision(decision_id, "operator-1", "security-lead")
    assert resp_del.status == "delegated"
    assert "security-lead" in resp_del.operator_notes

    # Assert explanation request
    resp_exp = await use_case.request_explanation(decision_id, "operator-1")
    assert resp_exp.id == str(decision_id)

    # Test history retrieval
    all_logs = await use_case.get_audit_history()
    assert len(all_logs) == 5  # approve, reject, simulate, delegate, explanation

@pytest.mark.asyncio
async def test_action_center_repositories_firestore() -> None:
    mock_client = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    
    from datetime import datetime, UTC
    now_str = datetime.now(UTC).isoformat()
    mock_doc.to_dict = MagicMock(return_value={
        "id": "00000000-0000-0000-0000-000000000000",
        "recommendation_id": "00000000-0000-0000-0000-000000000000",
        "priority": "medium",
        "severity": "medium",
        "confidence": 1.0,
        "expected_impact": "impact",
        "estimated_resolution_time": "10m",
        "required_resources": [],
        "human_approval_requirement": True,
        "suggested_action": "action",
        "explanation": "explanation",
        "status": "pending",
        "operator_notes": None,
        "created_at": now_str,
        "updated_at": now_str,
    })
    
    mock_get = AsyncMock(return_value=mock_doc)
    mock_client.collection().document().get = mock_get
    mock_client.collection().document().set = AsyncMock()
    
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = "00000000-0000-0000-0000-000000000000"
    mock_doc_ref.to_dict = mock_doc.to_dict
    mock_client.collection().get = AsyncMock(return_value=[mock_doc_ref])

    decision_repo = PendingDecisionRepository(mock_client)
    
    # Test save
    d = PendingDecision()
    await decision_repo.save(d)
    
    # Test get_by_id
    res = await decision_repo.get_by_id(d.id)
    assert res is not None
    
    # Test get_all
    all_d = await decision_repo.get_all()
    assert len(all_d) == 1

    # Test audit repo firestore
    mock_audit_doc = MagicMock()
    mock_audit_doc.id = "00000000-0000-0000-0000-000000000000"
    mock_audit_doc.to_dict = MagicMock(return_value={
        "id": "00000000-0000-0000-0000-000000000000",
        "decision_id": "00000000-0000-0000-0000-000000000000",
        "action": "approve",
        "operator_id": "operator-1",
        "timestamp": now_str,
        "details": "details",
    })
    mock_client.collection().get = AsyncMock(return_value=[mock_audit_doc])
    
    audit_repo = AuditLogRepository(mock_client)
    await audit_repo.save(AuditLog())
    res_audits = await audit_repo.get_by_decision_id(UUID("00000000-0000-0000-0000-000000000000"))
    assert len(res_audits) == 1
