import json
from typing import Any

from pydantic import BaseModel, Field

from app.intelligence import AIOrchestrator
from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion
from app.intelligence.structured_output import AIResponse


class PredictionItem(BaseModel):
    """A single prediction item containing prediction, confidence, reason, mitigation, and timeline."""

    prediction: str = Field(..., description="The predicted trend, state, or specific event description.")
    confidence: float = Field(..., description="The confidence level score from 0.0 to 1.0.")
    reason: str = Field(..., description="Explanation of why this prediction is made based on telemetry and incidents.")
    mitigation: str = Field(..., description="Recommended mitigation strategy or action to address the predicted risk.")
    timeline: str = Field(..., description="Expected time horizon or period of the predicted event (e.g., '17:30 - 18:00', 'Next 15 minutes').")


class StadiumPredictionsResponse(AIResponse):
    """Comprehensive Gemini-powered predictions for various aspects of stadium operations."""

    queue_growth: PredictionItem = Field(..., description="Forecasting queue changes and wait times at primary ticket/ingress points.")
    crowd_movement: PredictionItem = Field(..., description="Predicting spectator density flow, bottleneck zones, or congestion vectors.")
    volunteer_shortages: PredictionItem = Field(..., description="Assessing gaps in steward/volunteer allocation versus current/predicted demand.")
    medical_demand: PredictionItem = Field(..., description="Forecasting health/first-aid incidents due to overcrowding, heat, or specific events.")
    transport_congestion: PredictionItem = Field(..., description="Predicting traffic, rideshare queues, or transit delays around external zones.")
    gate_overload: PredictionItem = Field(..., description="Forecasting turnstile capacities, spectator ingress surges, or gate bottlenecks.")
    parking_saturation: PredictionItem = Field(..., description="Predicting fill rates and incoming parking/shuttle congestion.")
    weather_impact: PredictionItem = Field(..., description="Predicting operational changes or risks due to weather updates (e.g., rain, temperature, wind).")


class StadiumPredictionsPrompt(BasePrompt):
    """Structured prompt for the StadiumPredictionsAgent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="stadium_predictions_agent",
            description="Generates a comprehensive stadium predictions report.",
            author="System",
            tags=["agent", "predictions-assessment"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Predictive Intelligence AI Engine.\n"
                    "Analyze the following stadium inputs to forecast upcoming changes, risks, and mitigations:\n"
                    "- Operational State of Zones: {operational_state}\n"
                    "- Active Incidents: {incidents}\n"
                    "- Telemetry (Crowd Density & Queue Lengths): {telemetry}\n"
                    "- Weather Conditions: {weather}\n"
                    "- Current Recommended Actions: {recommendations}\n"
                    "- Matchday Timeline: {timeline}\n\n"
                    "Predict the following eight areas based on these data inputs:\n"
                    "1. Queue growth (ticket booth and gate queue expansion / shrinkage)\n"
                    "2. Crowd movement (density changes, bottlenecks, flow vectors between zones)\n"
                    "3. Volunteer shortages (steward gaps, unmanaged sectors)\n"
                    "4. Medical demand (heat exhaustion, crowd crushes, first aid needs)\n"
                    "5. Transport congestion (shuttles, rideshare lots, vehicle traffic)\n"
                    "6. Gate overload (turnstile backlogs, ingress surges, reader failures)\n"
                    "7. Parking saturation (lot fill rates, traffic lockups)\n"
                    "8. Weather impact (rain/temp effects on spectator comfort, delay risk, field conditions)\n\n"
                    "Provide a prediction, confidence level, reason, mitigation action, and expected timeline for each category.\n"
                    "Format your response to match the requested structured schema.\n"
                ),
            )
        ]
        super().__init__(metadata, versions)


class StadiumPredictionsAgent:
    """AI Agent responsible for compiling comprehensive predictive reports using Gemini."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_definition = StadiumPredictionsPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def generate_predictions(
        self,
        operational_state: dict[str, Any],
        incidents: list[dict[str, Any]],
        telemetry: dict[str, Any],
        weather: str,
        recommendations: list[dict[str, Any]],
        timeline: list[str],
    ) -> StadiumPredictionsResponse:
        """Calls the AI Orchestrator to generate structured predictions."""
        return await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=StadiumPredictionsResponse,
            operational_state=json.dumps(operational_state, default=str),
            incidents=json.dumps(incidents, default=str),
            telemetry=json.dumps(telemetry, default=str),
            weather=weather,
            recommendations=json.dumps(recommendations, default=str),
            timeline=json.dumps(timeline, default=str),
            min_confidence=0.0,
        )
