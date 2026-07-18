import json
from typing import Any

from app.application.scenario_simulator.models import Scenario, SimulationReport
from app.intelligence import AIOrchestrator
from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion


class ScenarioSimulatorPrompt(BasePrompt):
    """Structured prompt template for Scenario Simulator Agent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="scenario_simulator_agent",
            description="Analyzes the secondary impacts of simulated stadium operational scenarios.",
            author="System",
            tags=["agent", "simulation"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Scenario Simulator AI Agent.\n"
                    "Analyze the following hypothetical scenario: {scenario_type}\n"
                    "Scenario Details: {description}\n"
                    "Direct Deterministic Effects simulated: {direct_effects}\n"
                    "New Cloned Stadium Operational State: {cloned_state}\n"
                    "Review this context, evaluate secondary impacts, predicted bottlenecks, "
                    "resource utilization changes, risk score, confidence score, and recommended actions.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)

class ImpactAnalyzer:
    """Invokes the AI Orchestrator to run cognitive analysis on simulated scenario impacts."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_definition = ScenarioSimulatorPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def analyze(
        self,
        scenario: Scenario,
        cloned_state: Any,
        direct_effects: dict[str, Any],
    ) -> SimulationReport:
        """Invokes the AI Orchestrator to compute the simulation analysis report."""
        cloned_state_data = {
            "active_incidents": [str(i) for i in cloned_state.active_incidents],
            "crowd_conditions": {str(k): v for k, v in cloned_state.crowd_conditions.items()},
            "recommendations": [str(r) for r in cloned_state.recommendations],
            "volunteer_allocation": {str(k): str(v) for k, v in cloned_state.volunteer_allocation.items()},
            "queue_information": {str(k): v for k, v in cloned_state.queue_information.items()},
            "stadium_health": cloned_state.stadium_health,
        }

        # Convert state and effects to string formats
        state_str = json.dumps(cloned_state_data, indent=2, default=str)
        effects_str = json.dumps(direct_effects, indent=2)

        return await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=SimulationReport,
            scenario_type=scenario.scenario_type,
            description=scenario.description,
            direct_effects=effects_str,
            cloned_state=state_str,
            context="",
            min_confidence=0.0,
        )
