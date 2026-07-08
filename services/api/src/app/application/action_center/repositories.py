from typing import Dict, List, Optional
from uuid import UUID
from app.application.action_center.entities import PendingDecision, AuditLog

class PendingDecisionRepository:
    """Repository managing PendingDecision entities in memory or Firestore."""

    def __init__(self, firestore_client=None) -> None:
        self.client = firestore_client
        self._storage: Dict[UUID, PendingDecision] = {}

    async def get_by_id(self, decision_id: UUID) -> Optional[PendingDecision]:
        if self.client:
            doc = await self.client.collection("pending_decisions").document(str(decision_id)).get()
            if doc.exists:
                data = doc.to_dict()
                return self._map_to_decision(decision_id, data)
            return None
        return self._storage.get(decision_id)

    async def save(self, decision: PendingDecision) -> None:
        if self.client:
            await self.client.collection("pending_decisions").document(str(decision.id)).set(
                self._map_to_dict(decision)
            )
        else:
            self._storage[decision.id] = decision

    async def get_all(self) -> List[PendingDecision]:
        if self.client:
            docs = await self.client.collection("pending_decisions").get()
            return [self._map_to_decision(UUID(d.id), d.to_dict()) for d in docs]
        return list(self._storage.values())

    def _map_to_dict(self, d: PendingDecision) -> dict:
        return {
            "id": str(d.id),
            "recommendation_id": str(d.recommendation_id) if d.recommendation_id else None,
            "priority": d.priority,
            "severity": d.severity,
            "confidence": d.confidence,
            "expected_impact": d.expected_impact,
            "estimated_resolution_time": d.estimated_resolution_time,
            "required_resources": d.required_resources,
            "human_approval_requirement": d.human_approval_requirement,
            "suggested_action": d.suggested_action,
            "explanation": d.explanation,
            "status": d.status,
            "operator_notes": d.operator_notes,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat(),
        }

    def _map_to_decision(self, uid: UUID, data: dict) -> PendingDecision:
        from datetime import datetime
        rec_id = data.get("recommendation_id")
        return PendingDecision(
            id=uid,
            recommendation_id=UUID(rec_id) if rec_id else None,
            priority=data.get("priority", "medium"),
            severity=data.get("severity", "medium"),
            confidence=data.get("confidence", 1.0),
            expected_impact=data.get("expected_impact", ""),
            estimated_resolution_time=data.get("estimated_resolution_time", ""),
            required_resources=data.get("required_resources", []),
            human_approval_requirement=data.get("human_approval_requirement", True),
            suggested_action=data.get("suggested_action", ""),
            explanation=data.get("explanation", ""),
            status=data.get("status", "pending"),
            operator_notes=data.get("operator_notes"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )

class AuditLogRepository:
    """Repository managing AuditLog records."""

    def __init__(self, firestore_client=None) -> None:
        self.client = firestore_client
        self._storage: Dict[UUID, AuditLog] = {}

    async def save(self, log: AuditLog) -> None:
        if self.client:
            await self.client.collection("decision_audit_logs").document(str(log.id)).set(
                self._map_to_dict(log)
            )
        else:
            self._storage[log.id] = log

    async def get_by_decision_id(self, decision_id: UUID) -> List[AuditLog]:
        all_logs = await self.get_all()
        return [l for l in all_logs if l.decision_id == decision_id]

    async def get_all(self) -> List[AuditLog]:
        if self.client:
            docs = await self.client.collection("decision_audit_logs").get()
            return [self._map_to_log(UUID(d.id), d.to_dict()) for d in docs]
        return list(self._storage.values())

    def _map_to_dict(self, l: AuditLog) -> dict:
        return {
            "id": str(l.id),
            "decision_id": str(l.decision_id) if l.decision_id else None,
            "action": l.action,
            "operator_id": l.operator_id,
            "timestamp": l.timestamp.isoformat(),
            "details": l.details,
        }

    def _map_to_log(self, uid: UUID, data: dict) -> AuditLog:
        from datetime import datetime
        dec_id = data.get("decision_id")
        return AuditLog(
            id=uid,
            decision_id=UUID(dec_id) if dec_id else None,
            action=data.get("action", ""),
            operator_id=data.get("operator_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
            details=data.get("details", ""),
        )
