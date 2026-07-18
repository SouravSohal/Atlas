from datetime import UTC, datetime
from uuid import UUID, uuid4


class PendingDecision:
    """Domain entity representing an AI Decision awaiting human operator action."""

    def __init__(
        self,
        id: UUID | None = None,
        recommendation_id: UUID | None = None,
        priority: str = "medium",
        severity: str = "medium",
        confidence: float = 1.0,
        expected_impact: str = "",
        estimated_resolution_time: str = "",
        required_resources: list[str] | None = None,
        human_approval_requirement: bool = True,
        suggested_action: str = "",
        explanation: str = "",
        status: str = "pending",
        operator_notes: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid4()
        self.recommendation_id = recommendation_id
        self.priority = priority
        self.severity = severity
        self.confidence = confidence
        self.expected_impact = expected_impact
        self.estimated_resolution_time = estimated_resolution_time
        self.required_resources = required_resources or []
        self.human_approval_requirement = human_approval_requirement
        self.suggested_action = suggested_action
        self.explanation = explanation
        self.status = status
        self.operator_notes = operator_notes
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

class AuditLog:
    """Domain entity logging actions taken on pending decisions."""

    def __init__(
        self,
        id: UUID | None = None,
        decision_id: UUID | None = None,
        action: str = "",
        operator_id: str = "operator-1",
        timestamp: datetime | None = None,
        details: str = "",
    ) -> None:
        self.id = id or uuid4()
        self.decision_id = decision_id
        self.action = action
        self.operator_id = operator_id
        self.timestamp = timestamp or datetime.now(UTC)
        self.details = details
