from pydantic import BaseModel, Field


class AIStructuredOutput(BaseModel):
    """Base Pydantic model for structured AI outputs containing confidence and validation metadata."""

    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence level of the model output.")
    rationale: str = Field(..., description="Explanation of why this output was generated.")
