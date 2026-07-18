from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from atlas_core.domain.events.base import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DecisionApproved(DomainEvent):
    """Raised when an operator approves a decision."""
    decision_id: UUID
    operator_id: str
    recommendation_id: UUID | None = None

@dataclass(frozen=True, kw_only=True)
class DecisionRejected(DomainEvent):
    """Raised when an operator rejects a decision."""
    decision_id: UUID
    operator_id: str
    reason: str | None = None

@dataclass(frozen=True, kw_only=True)
class DecisionExplanationRequested(DomainEvent):
    """Raised when an operator requests additional reasoning."""
    decision_id: UUID
    operator_id: str

@dataclass(frozen=True, kw_only=True)
class DecisionSimulated(DomainEvent):
    """Raised when an operator runs a simulation on a decision."""
    decision_id: UUID
    operator_id: str
    parameters: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, kw_only=True)
class DecisionDelegated(DomainEvent):
    """Raised when an operator delegates a decision to another staff/division."""
    decision_id: UUID
    operator_id: str
    delegate_to: str
