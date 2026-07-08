from typing import Dict, List
from pydantic import BaseModel, Field
from app.intelligence.structured_output import AIResponse

class AllocationPlan(BaseModel):
    """Resource allocation quantities for volunteers, security, and medical staff."""
    volunteer_allocations: Dict[str, int] = Field(
        ...,
        description="Volunteers count to allocate mapped by zone ID."
    )
    security_allocations: Dict[str, int] = Field(
        ...,
        description="Security teams count to allocate mapped by zone ID."
    )
    medical_allocations: Dict[str, int] = Field(
        ...,
        description="Medical teams count to allocate mapped by zone ID."
    )
    active_gates: List[str] = Field(
        ...,
        description="List of gate zone IDs that should be open and active."
    )
    crowd_flow_directions: Dict[str, str] = Field(
        ...,
        description="Flow routing directions mapped by zone ID."
    )

class ResourceOptimizationResult(AIResponse):
    """Structured AI output of stadium resource optimizations and balances."""

    allocation_plan: AllocationPlan = Field(
        ...,
        description="The calculated optimal resource allocation plan."
    )
    expected_improvement: str = Field(
        ...,
        description="Description of expected improvement in wait times or density indicators."
    )
    confidence: float = Field(
        ...,
        description="Calculated confidence score from 0.0 to 1.0 of the optimization."
    )
    trade_offs: List[str] = Field(
        ...,
        description="Operational trade-offs associated with implementing this plan."
    )
