from datetime import UTC, datetime
from uuid import UUID
import structlog

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.value_objects.coordinates import Coordinates

from app.application.events import EventPublisher
from app.infrastructure.streaming.broadcast import BroadcastService
from app.application.action_center.entities import PendingDecision, AuditLog
from app.application.action_center.repositories import PendingDecisionRepository, AuditLogRepository
from app.application.action_center.dtos import PendingDecisionResponse, AuditLogResponse
from app.application.action_center.events import (
    DecisionApproved,
    DecisionRejected,
    DecisionExplanationRequested,
    DecisionSimulated,
    DecisionDelegated,
)

logger = structlog.get_logger()

class AIActionCenterUseCase:
    """Manages workflows inside the AI Action Center."""

    def __init__(
        self,
        decision_repo: PendingDecisionRepository,
        audit_repo: AuditLogRepository,
        state_repo: OperationalStateRepository[OperationalState],
        event_publisher: EventPublisher,
        broadcast_service: BroadcastService,
    ) -> None:
        self.decision_repo = decision_repo
        self.audit_repo = audit_repo
        self.state_repo = state_repo
        self.event_publisher = event_publisher
        self.broadcast_service = broadcast_service

    async def get_pending_decisions(self) -> list[PendingDecisionResponse]:
        """Retrieves all pending decisions."""
        decisions = await self.decision_repo.get_all()
        return [self._map_decision_to_response(d) for d in decisions]

    async def approve_decision(self, decision_id: UUID, operator_id: str) -> PendingDecisionResponse:
        """Approves a pending decision, records audits, publishes events, and updates operational state."""
        logger.info("Approving AI decision", decision_id=str(decision_id), operator_id=operator_id)
        decision = await self._get_decision_or_raise(decision_id)
        
        # 1. Update decision status
        decision.status = "approved"
        decision.updated_at = datetime.now(UTC)
        await self.decision_repo.save(decision)

        # 2. Record audit trail log
        audit = AuditLog(
            decision_id=decision_id,
            action="approve",
            operator_id=operator_id,
            details=f"Decision approved by operator {operator_id}. Action: {decision.suggested_action}."
        )
        await self.audit_repo.save(audit)

        # 3. Publish domain event
        event = DecisionApproved(
            aggregate_id=decision_id,
            decision_id=decision_id,
            operator_id=operator_id,
            recommendation_id=decision.recommendation_id
        )
        await self.event_publisher.publish_many([event])

        # 4. Update Operational State of the first zone to reflect real-time optimization
        states = await self.state_repo.get_all()
        if states:
            target_state = states[0]
            new_queue = max(1, target_state.queue_estimate.waiting_minutes - 3)
            target_state.update_state(
                new_density=target_state.density,
                new_queue_estimate=QueueEstimate(waiting_minutes=new_queue),
                location_coords=Coordinates(latitude=37.7749, longitude=-122.4194)
            )
            await self.state_repo.save(target_state)

        # 5. Broadcast to connected dashboards to refresh Mission Control
        await self.broadcast_service.broadcast_to_all({
            "event": "action_center_update",
            "action": "approved",
            "decision_id": str(decision_id)
        })

        return self._map_decision_to_response(decision)

    async def reject_decision(self, decision_id: UUID, operator_id: str, reason: str) -> PendingDecisionResponse:
        """Rejects a decision, recording audit parameters and updating dashboard connections."""
        logger.info("Rejecting AI decision", decision_id=str(decision_id), operator_id=operator_id)
        decision = await self._get_decision_or_raise(decision_id)

        decision.status = "rejected"
        decision.operator_notes = reason
        decision.updated_at = datetime.now(UTC)
        await self.decision_repo.save(decision)

        audit = AuditLog(
            decision_id=decision_id,
            action="reject",
            operator_id=operator_id,
            details=f"Decision rejected: {reason}."
        )
        await self.audit_repo.save(audit)

        event = DecisionRejected(
            aggregate_id=decision_id,
            decision_id=decision_id,
            operator_id=operator_id,
            reason=reason
        )
        await self.event_publisher.publish_many([event])

        await self.broadcast_service.broadcast_to_all({
            "event": "action_center_update",
            "action": "rejected",
            "decision_id": str(decision_id)
        })

        return self._map_decision_to_response(decision)

    async def request_explanation(self, decision_id: UUID, operator_id: str) -> PendingDecisionResponse:
        """Publishes domain events for explanations requested by human operators."""
        logger.info("Requesting explanation for AI decision", decision_id=str(decision_id), operator_id=operator_id)
        decision = await self._get_decision_or_raise(decision_id)

        audit = AuditLog(
            decision_id=decision_id,
            action="request_explanation",
            operator_id=operator_id,
            details="Operator requested deeper reasoning for the decision."
        )
        await self.audit_repo.save(audit)

        event = DecisionExplanationRequested(
            aggregate_id=decision_id,
            decision_id=decision_id,
            operator_id=operator_id
        )
        await self.event_publisher.publish_many([event])

        return self._map_decision_to_response(decision)

    async def simulate_decision(self, decision_id: UUID, operator_id: str, parameters: dict) -> PendingDecisionResponse:
        """Performs dynamic local density updates representing simulated forecasts."""
        logger.info("Simulating AI decision", decision_id=str(decision_id), operator_id=operator_id)
        decision = await self._get_decision_or_raise(decision_id)

        decision.status = "simulated"
        decision.updated_at = datetime.now(UTC)
        await self.decision_repo.save(decision)

        audit = AuditLog(
            decision_id=decision_id,
            action="simulate",
            operator_id=operator_id,
            details=f"Decision simulation executed with parameters: {parameters}."
        )
        await self.audit_repo.save(audit)

        event = DecisionSimulated(
            aggregate_id=decision_id,
            decision_id=decision_id,
            operator_id=operator_id,
            parameters=parameters
        )
        await self.event_publisher.publish_many([event])

        states = await self.state_repo.get_all()
        if states:
            target_state = states[0]
            new_density = max(0.1, target_state.density.value - 0.1)
            target_state.update_state(
                new_density=CrowdDensity(value=new_density),
                new_queue_estimate=target_state.queue_estimate,
                location_coords=Coordinates(latitude=37.7749, longitude=-122.4194)
            )
            await self.state_repo.save(target_state)

        await self.broadcast_service.broadcast_to_all({
            "event": "action_center_update",
            "action": "simulated",
            "decision_id": str(decision_id)
        })

        return self._map_decision_to_response(decision)

    async def delegate_decision(self, decision_id: UUID, operator_id: str, delegate_to: str) -> PendingDecisionResponse:
        """Delegates decision workflows to designated units."""
        logger.info("Delegating AI decision", decision_id=str(decision_id), operator_id=operator_id, delegate_to=delegate_to)
        decision = await self._get_decision_or_raise(decision_id)

        decision.status = "delegated"
        decision.operator_notes = f"Delegated to: {delegate_to}"
        decision.updated_at = datetime.now(UTC)
        await self.decision_repo.save(decision)

        audit = AuditLog(
            decision_id=decision_id,
            action="delegate",
            operator_id=operator_id,
            details=f"Decision delegated to: {delegate_to}."
        )
        await self.audit_repo.save(audit)

        event = DecisionDelegated(
            aggregate_id=decision_id,
            decision_id=decision_id,
            operator_id=operator_id,
            delegate_to=delegate_to
        )
        await self.event_publisher.publish_many([event])

        await self.broadcast_service.broadcast_to_all({
            "event": "action_center_update",
            "action": "delegated",
            "decision_id": str(decision_id)
        })

        return self._map_decision_to_response(decision)

    async def get_audit_history(self, decision_id: UUID | None = None) -> list[AuditLogResponse]:
        """Returns log logs mapping operator actions."""
        if decision_id:
            logs = await self.audit_repo.get_by_decision_id(decision_id)
        else:
            logs = await self.audit_repo.get_all()
        return [self._map_log_to_response(l) for l in logs]

    async def _get_decision_or_raise(self, decision_id: UUID) -> PendingDecision:
        decision = await self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise ValueError(f"Pending decision {decision_id} not found.")
        return decision

    def _map_decision_to_response(self, d: PendingDecision) -> PendingDecisionResponse:
        return PendingDecisionResponse(
            id=str(d.id),
            recommendation_id=str(d.recommendation_id) if d.recommendation_id else None,
            priority=d.priority,
            severity=d.severity,
            confidence=d.confidence,
            expected_impact=d.expected_impact,
            estimated_resolution_time=d.estimated_resolution_time,
            required_resources=d.required_resources,
            human_approval_requirement=d.human_approval_requirement,
            suggested_action=d.suggested_action,
            explanation=d.explanation,
            status=d.status,
            operator_notes=d.operator_notes,
            created_at=d.created_at.isoformat(),
            updated_at=d.updated_at.isoformat(),
        )

    def _map_log_to_response(self, l: AuditLog) -> AuditLogResponse:
        return AuditLogResponse(
            id=str(l.id),
            decision_id=str(l.decision_id),
            action=l.action,
            operator_id=l.operator_id,
            timestamp=l.timestamp.isoformat(),
            details=l.details,
        )
