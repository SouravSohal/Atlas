from typing import Dict
from pydantic import Field
from app.intelligence.structured_output import AIResponse

class PredictionResult(AIResponse):
    """Structured AI forecasting and prediction report for stadium operations."""

    predicted_crowd_density: Dict[str, float] = Field(
        ...,
        description="Predicted crowd density percentage index (0.0 to 1.0) mapped by zone ID."
    )
    predicted_queue_length: Dict[str, int] = Field(
        ...,
        description="Predicted turnstile wait time queue lengths in minutes mapped by zone ID."
    )
    incident_probability: Dict[str, float] = Field(
        ...,
        description="Predicted probability score (0.0 to 1.0) of new operational incidents mapped by zone ID."
    )
    volunteer_demand: Dict[str, int] = Field(
        ...,
        description="Recommended staffing demand count for volunteers mapped by zone ID."
    )
    gate_utilization: Dict[str, float] = Field(
        ...,
        description="Predicted turnstile gate utilization capacity percentage (0.0 to 1.0) mapped by gate zone ID."
    )
    explanation: str = Field(
        ...,
        description="Professional AI narrative explaining predicted spectator congestion, wait bottlenecks, and staff demands."
    )
