from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion

class DecisionEnginePrompt(BasePrompt):
    """Structured prompt template for the AI Decision Engine."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="decision_engine_agent",
            description="Enhances pre-generated business recommendations into structured decisions.",
            author="System",
            tags=["agent", "decision", "engine"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Decision Engine AI Agent.\n"
                    "We have deterministic business recommendations that require AI enhancement:\n"
                    "Recommendations: {recommendations}\n"
                    "Operational State: {operational_state}\n"
                    "Active Incidents: {incidents}\n\n"
                    "Evaluate each recommendation. Provide a prioritized operational decision with priority, "
                    "severity, confidence, expected impact, estimated resolution time, required resources, human approval requirements, "
                    "suggested operator action, and a concise explanation.\n"
                    "NEVER generate decisions for which there is no matching deterministic business recommendation.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
