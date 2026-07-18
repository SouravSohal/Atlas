import json
from typing import Any

from pydantic import BaseModel, Field

from app.intelligence import AIOrchestrator
from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion
from app.intelligence.structured_output import AIResponse


class PrioritizedRecommendationItem(BaseModel):
    """Represents an input business recommendation prioritized and explained by the AI agent."""

    recommendation_id: str = Field(..., description="ID of the pre-generated business recommendation.")
    action_type: str = Field(..., description="The type of action recommended.")
    priority_order: int = Field(..., description="The priority order of the action (e.g. 1, 2, 3).")
    priority_level: str = Field(..., description="Low, Medium, High, Critical")
    explanation: str = Field(..., description="Contextual explanation for why this action is prioritized at this level.")


class RecommendationAgentResponse(AIResponse):
    """Structured response containing explanations, priority ranking, risks, and alternatives."""

    natural_language_explanation: str = Field(..., description="Natural language summary/explanation of the stadium state.")
    prioritized_recommendations: list[PrioritizedRecommendationItem] = Field(..., description="List of pre-generated business recommendations rank-prioritized.")
    risk_assessment: str = Field(..., description="Analysis of risks associated with current operational conditions and incidents.")
    alternative_actions: list[str] = Field(default_factory=list, description="Alternative actions to consider if recommendations cannot be executed.")


class RecommendationAgentPrompt(BasePrompt):
    """Structured prompt component for the RecommendationAgent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="recommendation_agent",
            description="Explains, prioritizes, and assesses risks for business recommendations.",
            author="System",
            tags=["agent", "recommendations"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS FIFA World Cup 2026 Stadium Operations AI Agent.\n"
                    "Analyze the following operational conditions and the pre-generated tournament/stadium recommendations.\n"
                    "Your job is ONLY to prioritize, explain, and summarize them, and provide a security and logistics risk assessment.\n"
                    "Ensure risk assessments reference tournament timelines, crowd ingress/egress safety, volunteer staffing, "
                    "and emergency response protocols. DO NOT generate new recommendations from scratch.\n"
                    "Format your response to match the requested schema.\n"
                    "Operational Conditions: {context}\n"
                    "Pre-generated Business Recommendations: {business_recs}\n"
                )
            )
        ]
        super().__init__(metadata, versions)


class RecommendationAgent:
    """AI Agent responsible for explaining, prioritizing, and assessing risks for pre-generated recommendations."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_definition = RecommendationAgentPrompt()

        # Register the prompt in the orchestrator's registry during initialization
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def analyze_recommendations(
        self,
        operational_state_summary: dict[str, Any],
        incidents: list[dict[str, Any]],
        business_recommendations: list[dict[str, Any]],
    ) -> RecommendationAgentResponse:
        """Invokes the AI Orchestrator to explain and prioritize pre-generated recommendations."""
        # 1. Compile context data and format as JSON
        context_data = {
            "operational_state": operational_state_summary,
            "incidents": incidents,
        }
        context_str = json.dumps(context_data, indent=2, default=str)

        # 2. Serialize pre-generated business recommendations
        business_recs_str = json.dumps(business_recommendations, indent=2, default=str)

        # 3. Execute prompt template via AIOrchestrator
        return await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=RecommendationAgentResponse,
            business_recs=business_recs_str,
            # We inject the operational context directly into PromptBuilder as variable
            context=context_str,
            min_confidence=0.0,
        )
