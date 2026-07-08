from typing import List, Optional
from pydantic import BaseModel, Field

class PendingDecisionResponse(BaseModel):
    """Details of a pending operations decision awaiting human approval."""
    id: str = Field(..., description="Unique ID of the decision.")
    recommendation_id: Optional[str] = Field(None, description="Associated recommendation ID.")
    priority: str = Field(..., description="Priority scale.")
    severity: str = Field(..., description="Severity scale.")
    confidence: float = Field(..., description="Confidence index (0.0 to 1.0).")
    expected_impact: str = Field(..., description="Expected impact description.")
    estimated_resolution_time: str = Field(..., description="Estimated time to complete.")
    required_resources: List[str] = Field(..., description="List of required resource roles.")
    human_approval_requirement: bool = Field(..., description="True if operator sign-off is required.")
    suggested_action: str = Field(..., description="Specific action detail.")
    explanation: str = Field(..., description="Explanation of why this action is suggested.")
    status: str = Field(..., description="Current state (pending, approved, rejected, delegated).")
    operator_notes: Optional[str] = Field(None, description="Notes written by the operator.")
    created_at: str = Field(..., description="Creation date.")
    updated_at: str = Field(..., description="Last modification date.")

class AuditLogResponse(BaseModel):
    """Auditing entry detailing decisions taken by operators."""
    id: str = Field(..., description="Unique ID of the audit log.")
    decision_id: str = Field(..., description="Associated decision ID.")
    action: str = Field(..., description="Action type performed (e.g. approve, reject).")
    operator_id: str = Field(..., description="ID of the operator who executed the action.")
    timestamp: str = Field(..., description="Date and time when the event occurred.")
    details: str = Field(..., description="Audit trace detail narrative.")
