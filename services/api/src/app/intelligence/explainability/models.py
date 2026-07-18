
from pydantic import Field

from app.intelligence.structured_output import AIResponse


class RecommendationExplanation(AIResponse):
    """Structured AI explanation of a specific operational recommendation."""

    why_recommendation: str = Field(
        ...,
        description="Clear, concise explanation detailing why this recommendation is proposed."
    )
    evidence_considered: list[str] = Field(
        ...,
        description="Key telemetry evidence items considered (e.g. gates bottleneck, medical emergencies)."
    )
    business_rules_triggered: list[str] = Field(
        ...,
        description="Identifiers of safety/operational business rules triggered by the current state."
    )
    operational_data_used: list[str] = Field(
        ...,
        description="Specific operational data metrics utilized (e.g. waiting time, density index)."
    )
    confidence: float = Field(
        ...,
        description="Estimated confidence level score from 0.0 to 1.0 of the proposed solution."
    )
    alternative_actions: list[str] = Field(
        ...,
        description="Alternative backup actions evaluated during reasoning."
    )
    trade_offs: list[str] = Field(
        ...,
        description="Critical trade-offs associated with implementing this recommendation."
    )
    limitations: list[str] = Field(
        ...,
        description="Limitations or potential side-effects of this action."
    )
