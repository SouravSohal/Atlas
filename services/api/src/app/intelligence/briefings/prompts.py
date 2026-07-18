from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion


class ExecutiveBriefingPrompt(BasePrompt):
    """Structured prompt template for Executive Briefing Agent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="executive_briefing_agent",
            description="Generates high-level executive operational briefings and summary dashboards.",
            author="System",
            tags=["agent", "briefing", "executive"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Executive Briefing AI Agent.\n"
                    "Generate a professional executive briefing of type: {briefing_type}\n"
                    "Here is the aggregated operational KPI telemetry: {kpis}\n"
                    "Here is the list of active/recent incidents: {incidents}\n"
                    "Evaluate this information and generate a structured briefing including executive summary, "
                    "operational highlights, major incidents details, AI recommendations, risk assessment, and suggested next actions.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
