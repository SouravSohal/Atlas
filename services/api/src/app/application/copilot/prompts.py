from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion

class CopilotPrompt(BasePrompt):
    """Structured prompt template for ATLAS Copilot Agent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="atlas_copilot_agent",
            description="Stadium operations cognitive companion.",
            author="System",
            tags=["agent", "copilot", "chat"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are ATLAS Copilot, the AI-first operational assistant for stadium management.\n"
                    "Respond to the user's operational query: {message}\n"
                    "Response Language: {language}\n"
                    "Conversation History:\n"
                    "{history}\n\n"
                    "Live Telemetry Context:\n"
                    "{telemetry_context}\n\n"
                    "Synthesize a helpful response. Do not invent facts outside the context. "
                    "Support markdown rendering and add citations (e.g. '[Incident #inc_id]') when referencing live items.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
