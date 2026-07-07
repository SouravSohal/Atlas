from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """Generic base class for structured AI response payloads."""

    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")
    rationale: str = Field(..., description="The rationale or reasoning behind the generated output.")


class AIRecommendation(AIResponse):
    """Structured output for recommendations."""

    action_type: str = Field(..., description="Proposed operational action.")
    priority: str = Field(..., description="Calculated priority level (low, medium, high, critical).")
    details: str = Field(..., description="Detailed instructions or actions to take.")


class AIExplanation(AIResponse):
    """Structured output for explaining anomalies or situations."""

    root_cause: str = Field(..., description="Identified root cause.")
    impact_analysis: str = Field(..., description="Potential operational impact details.")
    mitigation_steps: list[str] = Field(default_factory=list, description="Recommended immediate mitigation actions.")


class AISummary(AIResponse):
    """Structured output for summaries."""

    summary: str = Field(..., description="Brief textual summary.")
    key_points: list[str] = Field(default_factory=list, description="Key points extracted from the context.")
    threat_level: str = Field(..., description="Threat assessment level.")


class AIPrediction(AIResponse):
    """Structured output for predictive telemetry or states."""

    predicted_value: str = Field(..., description="The predicted state or value.")
    probability: float = Field(..., ge=0.0, le=1.0, description="Estimated probability of the prediction.")
    time_horizon: str = Field(..., description="Time horizon for the prediction.")


class ResponseEnvelope[T: BaseModel](BaseModel):
    """Wrapper encapsulating the structured AI output with processing trace and metadata."""

    trace_id: str = Field(..., description="Correlation ID for tracing the AI pipeline execution.")
    model_name: str = Field(..., description="Name of the model that generated the response.")
    prompt_version: str = Field(..., description="Version of the prompt template used.")
    execution_time_ms: float = Field(..., description="Execution time of the model call in milliseconds.")
    data: T = Field(..., description="The validated structured response payload.")
