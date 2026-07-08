import json
import time
from typing import List

from app.intelligence import AIOrchestrator
from app.application.operational_state.state_manager import OperationalStateManager
from app.application.copilot.models import CopilotChatRequest, CopilotChatResponse
from app.application.copilot.prompts import CopilotPrompt

class CopilotService:
    """Manages context retrieval and orchestrates ATLAS Copilot conversation generation."""

    def __init__(self, orchestrator: AIOrchestrator, state_manager: OperationalStateManager) -> None:
        self.orchestrator = orchestrator
        self.state_manager = state_manager
        self.prompt_definition = CopilotPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def chat(self, request: CopilotChatRequest) -> CopilotChatResponse:
        """Loads state snapshots, formats history records, and triggers orchestrator chat queries."""
        start_time = time.perf_counter()

        # 1. Fetch live telemetry context
        snapshot = await self.state_manager.get_snapshot()
        
        telemetry_data = {
            "active_incidents": [str(i) for i in snapshot.active_incidents],
            "crowd_conditions": {str(k): v for k, v in snapshot.crowd_conditions.items()},
            "recommendations": [str(r) for r in snapshot.recommendations],
            "volunteer_allocation": {str(k): str(v) for k, v in snapshot.volunteer_allocation.items()},
            "queue_information": {str(k): v for k, v in snapshot.queue_information.items()},
            "stadium_health": snapshot.stadium_health,
        }
        telemetry_str = json.dumps(telemetry_data, indent=2, default=str)

        # 2. Format history
        history_lines = []
        for msg in request.history:
            history_lines.append(f"{msg.role.upper()}: {msg.text}")
        history_str = "\n".join(history_lines) if history_lines else "No history."

        # 3. Execute AI Orchestrator
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=CopilotChatResponse,
            message=request.message,
            language=request.language,
            history=history_str,
            telemetry_context=telemetry_str,
            context="",
            min_confidence=0.0,
        )

        end_time = time.perf_counter()
        execution_time_ms = int((end_time - start_time) * 1000)

        # Enforce execution time and model version on the structured response
        report.execution_time_ms = execution_time_ms
        report.model_version = "Gemini 2.5 Flash"

        return report
