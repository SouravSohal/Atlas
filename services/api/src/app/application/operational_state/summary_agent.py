import json
from typing import Any

from pydantic import Field

from app.intelligence import AIOrchestrator
from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion
from app.intelligence.structured_output import AIResponse


class SituationSummaryAgentResponse(AIResponse):
    """Structured response containing executive summary, situation assessment, immediate risks, recommended actions, predicted outcomes, confidence score, assumptions, and alternative strategies."""

    executive_summary: str = Field(..., description="High-level executive summary of the stadium's operational situation.")
    situation_assessment: str = Field(..., description="Comprehensive situation assessment of the stadium.")
    immediate_risks: list[str] = Field(..., description="List of immediate risks identified in the stadium.")
    recommended_actions: list[str] = Field(..., description="List of recommended actions to take immediately.")
    predicted_outcome: str = Field(..., description="Predicted outcome of the current situation if recommendations are or are not executed.")
    confidence_score: float = Field(..., description="Confidence score between 0.0 and 1.0 representing the AI's certainty in this analysis.")
    assumptions: list[str] = Field(..., description="List of key assumptions made during this situation assessment.")
    alternative_strategies: list[str] = Field(..., description="Alternative backup strategies or contingency plans.")


class SituationSummaryAgentPrompt(BasePrompt):
    """Structured prompt for the SituationSummaryAgent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="situation_summary_agent",
            description="Generates a comprehensive stadium situation assessment report.",
            author="System",
            tags=["agent", "situation-assessment"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Situation Analysis Engine.\n"
                    "Analyze the following inputs representing the current state of the stadium:\n"
                    "- Operational State: {operational_state}\n"
                    "- Active Incidents: {incidents}\n"
                    "- Telemetry (Crowd Density & Queue Lengths): {telemetry}\n"
                    "- Weather Conditions: {weather}\n"
                    "- Recommended Actions: {recommendations}\n"
                    "- Matchday Timeline: {timeline}\n\n"
                    "Your job is to generate a structured situation report detailing the executive summary, situation assessment, immediate risks, recommended actions, predicted outcomes, confidence, assumptions, and alternative strategies.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)


class SituationSummaryAgent:
    """AI Agent responsible for compiling high-level stadium situation reports."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_definition = SituationSummaryAgentPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def generate_summary(
        self,
        operational_state: dict[str, Any],
        incidents: list[dict[str, Any]],
        telemetry: dict[str, Any],
        weather: str,
        recommendations: list[dict[str, Any]],
        timeline: list[str],
    ) -> SituationSummaryAgentResponse:
        """Calls the AI Orchestrator to generate structured situation summaries."""
        return await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=SituationSummaryAgentResponse,
            operational_state=json.dumps(operational_state, default=str),
            incidents=json.dumps(incidents, default=str),
            telemetry=json.dumps(telemetry, default=str),
            weather=weather,
            recommendations=json.dumps(recommendations, default=str),
            timeline=json.dumps(timeline, default=str),
            min_confidence=0.0,
        )
