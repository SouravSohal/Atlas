import json
import structlog
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.intelligence.model_gateway import ModelGateway

logger = structlog.get_logger()

class StadiumAIResponse(BaseModel):
    """Structured executive AI response for the stadium operations team. Excludes chain-of-thought steps."""
    executive_summary: str = Field(description="High-level operational overview of Aurelia Arena.")
    predictions: List[str] = Field(description="AI predictive statements regarding crowd density, queue waits, and risk cascades.")
    explanation: str = Field(description="Natural language breakdown explaining why current recommendations were generated.")
    risk_assessment: List[str] = Field(description="Prioritized threat vectors and potential cascading propagation risks.")
    decision_justification: str = Field(description="Cognitive justification for the approved safety and routing actions.")

class StadiumAIOrchestrator:
    """Orchestrator that compiles stadium digital twin states and invokes Gemini for structured operations briefings."""

    def __init__(self, gateway: ModelGateway) -> None:
        self.gateway = gateway

    async def generate_briefing(
        self,
        stadium_state: Dict[str, Any],
        active_incidents: List[Dict[str, Any]],
        telemetry: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        timeline: List[str],
        graph_summary: Dict[str, Any]
    ) -> StadiumAIResponse:
        """Assembles variables into the prompt context and queries Gemini for a structured response schema."""
        logger.info(
            "Generating AI Stadium Briefing",
            incidents_count=len(active_incidents),
            recs_count=len(recommendations)
        )

        prompt = f"""
You are the ATLAS Stadium Operations Intelligence Brain.
You are given the active state parameters of the Aurelia Arena digital twin below.

---
[CURRENT STADIUM STATE]
{json.dumps(stadium_state, indent=2)}

[ACTIVE INCIDENTS]
{json.dumps(active_incidents, indent=2)}

[TELEMETRY SNAPSHOT]
{json.dumps(telemetry, indent=2)}

[RECOMMENDATIONS TRIGGERED]
{json.dumps(recommendations, indent=2)}

[MATCHDAY PLAYBACK TIMELINE]
{json.dumps(timeline, indent=2)}

[GRAPH TOPOLOGY SUMMARY]
{json.dumps(graph_summary, indent=2)}
---

Task:
Analyze the operational state, active safety incidents, queue backups, and edge flows.
Provide the operations dispatchers with a structured executive summary, future density predictions, natural language recommendations explanation, a cascading risk assessment, and decision justification.

Constraints:
- Respond STRICTLY conforming to the schema requested.
- Do NOT output any preamble, markdown wrapper (like ```json), or raw thinking steps.
- Exclude any internal chain-of-thought blocks.
"""

        raw_json_str = await self.gateway.generate_response(
            prompt=prompt,
            response_schema=StadiumAIResponse
        )

        # Parse JSON and validate model
        parsed_dict = json.loads(raw_json_str)
        return StadiumAIResponse.model_validate(parsed_dict)
