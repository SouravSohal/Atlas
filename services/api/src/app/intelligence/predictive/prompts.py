from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion


class PredictiveIntelligencePrompt(BasePrompt):
    """Structured prompt template for predictive intelligence agent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="predictive_intelligence_agent",
            description="Explains computed predictive stadium telemetry metrics.",
            author="System",
            tags=["agent", "predictive", "forecasting"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Predictive Intelligence AI Agent.\n"
                    "We have computed the following deterministic operational predictions:\n"
                    "Predicted Crowd Density: {predicted_density}\n"
                    "Predicted Wait Queue Times: {predicted_queues}\n"
                    "Predicted Incident Probabilities: {incident_probs}\n"
                    "Predicted Volunteer Staff Demands: {volunteer_demands}\n"
                    "Predicted Ingress Gate Utilizations: {gate_utilizations}\n\n"
                    "Analyze these calculated parameters and write a professional executive explanation of the "
                    "forecasted operational risk trends, queue safety thresholds, and volunteer allocation balance.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
