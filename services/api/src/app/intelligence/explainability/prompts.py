from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion

class ExplainabilityPrompt(BasePrompt):
    """Structured prompt template for explainability engine."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="explainability_agent",
            description="Justifies recommendations using stadium operational states.",
            author="System",
            tags=["agent", "explainability", "justification"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations AI Explainability Agent.\n"
                    "Provide a concise, user-facing explanation for the following recommendation:\n"
                    "Recommendation Action: {action}\n"
                    "Priority: {priority}\n"
                    "Collected Evidence: {evidence}\n"
                    "Operational Data: {operational_data}\n\n"
                    "Structure your output to include why this recommendation, evidence considered, "
                    "business rules triggered, operational data used, confidence, alternative actions, trade-offs, and limitations.\n"
                    "Do NOT output any chain-of-thought or reasoning steps. Output only concise user-facing responses.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
