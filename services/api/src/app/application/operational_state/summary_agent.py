import json
from typing import Any

from pydantic import Field

from app.intelligence import AIOrchestrator
from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion
from app.intelligence.structured_output import AIResponse


class SituationSummaryAgentResponse(AIResponse):
    """Structured response containing executive, operational, security, and medical summaries."""

    executive_summary: str = Field(..., description="High-level executive summary of the stadium's operational situation.")
    operations_summary: str = Field(..., description="Details regarding queue times, gate statuses, and operational flow.")
    security_summary: str = Field(..., description="Summary of security incidents, crowd densities, and threat levels.")
    medical_summary: str = Field(..., description="Summary of medical issues and first responder status.")


class SituationSummaryAgentPrompt(BasePrompt):
    """Structured prompt for the SituationSummaryAgent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="situation_summary_agent",
            description="Generates executive, operations, security, and medical summaries.",
            author="System",
            tags=["agent", "summary"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Executive Summary AI Agent.\n"
                    "Analyze the following operational snapshot, including operational state, incidents, crowd conditions, volunteer status, and recommendations.\n"
                    "Your job is to generate a structured situation report detailing executive, operations, security, and medical aspects.\n"
                    "Format your response to match the requested schema.\n"
                    "Stadium Operational Snapshot: {snapshot}\n"
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
        operational_state_summary: dict[str, Any],
        incidents: list[dict[str, Any]],
        crowd_conditions: dict[str, float],
        volunteer_status: dict[str, Any],
        recommendations: list[dict[str, Any]],
    ) -> SituationSummaryAgentResponse:
        """Calls the AI Orchestrator to generate structured situation summaries."""
        # Compile snapshot as JSON
        snapshot_data = {
            "operational_state": operational_state_summary,
            "incidents": incidents,
            "crowd_conditions": crowd_conditions,
            "volunteer_status": volunteer_status,
            "recommendations": recommendations,
        }
        snapshot_str = json.dumps(snapshot_data, indent=2, default=str)

        return await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=SituationSummaryAgentResponse,
            snapshot=snapshot_str,
            context="",
            min_confidence=0.0,
        )
