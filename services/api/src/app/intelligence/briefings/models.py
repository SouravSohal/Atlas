from typing import List, Dict, Any
from pydantic import Field
from app.intelligence.structured_output import AIResponse

class BriefingReport(AIResponse):
    """Structured response containing professional executive operational briefing details."""

    executive_summary: str = Field(
        ...,
        description="High-level, professional executive summary outlining current stadium operational posture."
    )
    key_metrics: Dict[str, Any] = Field(
        ...,
        description="Key metrics and operational KPI data points aggregated for executive review."
    )
    operational_highlights: List[str] = Field(
        ...,
        description="List of key operational achievements, milestones, or successful crowd maneuvers."
    )
    major_incidents: List[str] = Field(
        ...,
        description="List of major security, medical, or facility incidents currently active or resolved during this shift."
    )
    ai_recommendations: List[str] = Field(
        ...,
        description="Strategic recommendations computed by the cognitive engine to optimize ingress/egress and staffing."
    )
    risk_assessment: str = Field(
        ...,
        description="Overall risk assessment rating and qualitative risk narrative (e.g. Low, Medium, High risk factors)."
    )
    suggested_next_actions: List[str] = Field(
        ...,
        description="Immediate actionable next items or dispatch orders recommended for executive approval."
    )
