from dataclasses import dataclass, field
from typing import Any

from pydantic import Field

from app.intelligence.structured_output import AIResponse


class DecisionItem(AIResponse):
    """An enhanced stadium operations decision generated from a business recommendation."""

    original_recommendation_id: str = Field(
        ...,
        description="ID of the original deterministic business recommendation."
    )
    priority: str = Field(
        ...,
        description="Priority scaling (e.g. low, medium, high, critical)."
    )
    severity: str = Field(
        ...,
        description="Severity scaling of the underlying incident/condition."
    )
    confidence: float = Field(
        ...,
        description="Confidence parameter from 0.0 to 1.0."
    )
    expected_impact: str = Field(
        ...,
        description="Expected operational impact of implementing this decision."
    )
    estimated_resolution_time: str = Field(
        ...,
        description="Estimated time required to execute and resolve (e.g. 10 minutes)."
    )
    required_resources: list[str] = Field(
        ...,
        description="List of required staff roles or materials."
    )
    human_approval_requirement: bool = Field(
        ...,
        description="True if human operator validation is required before dispatching."
    )
    suggested_operator_action: str = Field(
        ...,
        description="Action instructions for the operator."
    )
    explanation: str = Field(
        ...,
        description="AI justification explaining why this decision enhances the recommendation."
    )

class DecisionEngineResult(AIResponse):
    """Container holding prioritized enhanced decisions and engine details."""

    decisions: list[DecisionItem] = Field(
        ...,
        description="Prioritized list of operations decisions."
    )
    model_version: str = Field(
        ...,
        description="Model version utilized for routing."
    )
    execution_time_ms: int = Field(
        ...,
        description="Engine processing duration in milliseconds."
    )

@dataclass
class DecisionContext:
    """Holds operational inputs passed to the decision engine."""
    operational_state: dict[str, Any] = field(default_factory=dict)
    incidents: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
