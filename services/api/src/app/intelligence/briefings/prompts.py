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
                    "You are the ATLAS FIFA World Cup 2026 Stadium Operations Executive Briefing AI Agent.\n"
                    "Generate a professional tournament operational briefing of type: {briefing_type}\n"
                    "Here is the aggregated operational KPI telemetry: {kpis}\n"
                    "Here is the list of active/recent stadium incidents: {incidents}\n"
                    "Evaluate this information and generate a structured briefing including executive summary, "
                    "match-day highlights, major safety/incident details, tournament logistics recommendations, risk assessment, "
                    "and tactical emergency response actions.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
