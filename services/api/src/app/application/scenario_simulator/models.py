from datetime import datetime
from uuid import UUID, uuid4
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from app.intelligence.structured_output import AIResponse

class Scenario(BaseModel):
    """Configuration for a hypothetical stadium operational simulation scenario."""
    id: UUID = Field(default_factory=uuid4)
    scenario_type: str = Field(..., description="Type of scenario (e.g., Gate Closure, Crowd Surge, Evacuation).")
    zone_id: Optional[UUID] = Field(None, description="The primary zone affected by this scenario.")
    severity: str = Field("medium", description="Severity level: low, medium, high, critical.")
    description: str = Field(..., description="Detailed description of the hypothetical event.")
    params: dict[str, Any] = Field(default_factory=dict, description="Additional custom parameters for simulation.")

class SimulationReport(AIResponse):
    """Structured AI report predicting impacts of a hypothetical simulation scenario."""
    operational_impact: str = Field(..., description="High-level description of the scenario's operational impact.")
    estimated_queue_changes: str = Field(..., description="Details regarding predicted queue length variations.")
    resource_utilization: str = Field(..., description="Summary of resource allocation and deployment requirements.")
    risk_score: float = Field(..., description="Evaluated risk score from 0.0 (safe) to 1.0 (extremely critical).")
    recommended_actions: List[str] = Field(..., description="List of immediate tactical recommendations.")
    confidence_score: float = Field(..., description="Confidence index of the AI model analysis.")
    predicted_bottlenecks: List[str] = Field(..., description="List of predicted zone bottlenecks or congestion clusters.")

class SimulationRecord(BaseModel):
    """Log record of a simulated scenario execution."""
    id: UUID = Field(default_factory=uuid4)
    scenario: Scenario
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    report: SimulationReport
    direct_effects: dict[str, Any]
