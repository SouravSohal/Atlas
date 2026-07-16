import json
import time
from typing import List, Any
from uuid import uuid4
from datetime import datetime, UTC

from app.intelligence import AIOrchestrator
from app.application.operational_state.state_manager import OperationalStateManager
from app.application.copilot.models import CopilotChatRequest, CopilotChatResponse
from app.application.copilot.prompts import CopilotPrompt


class CopilotService:
    """Manages context retrieval and orchestrates ATLAS Copilot conversation generation with full memory."""

    def __init__(self, orchestrator: AIOrchestrator, state_manager: OperationalStateManager, event_repo: Any) -> None:
        self.orchestrator = orchestrator
        self.state_manager = state_manager
        self.event_repo = event_repo
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

        # 1. Fetch live telemetry/snapshot
        snapshot = await self.state_manager.get_snapshot()

        # 2. Fetch active incidents (resolved = False)
        incidents = await self.state_manager.incident_repo.list()
        active_incidents = [inc for inc in incidents if not inc.resolved]
        incidents_data = [
            {
                "id": str(i.id),
                "incident_type": i.incident_type.value,
                "severity": i.severity.value,
                "description": i.description,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in active_incidents
        ]

        # 3. Fetch operator decisions and recent recommendations
        recs = await self.state_manager.recommendation_repo.list()
        operator_decisions = [
            {
                "action_type": r.action_type,
                "priority": r.priority.value,
                "status": r.status.value,
                "approved_by_id": str(r.approved_by_id) if r.approved_by_id else None,
                "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            }
            for r in recs
            if r.status.value in ("approved", "rejected", "executing", "completed")
        ]

        recent_recommendations = [
            {
                "action_type": r.action_type,
                "priority": r.priority.value,
                "status": r.status.value,
                "confidence": r.confidence.value,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in recs
            if r.status.value == "pending"
        ]

        # 4. Fetch timeline logs
        events = await self.event_repo.list()
        timeline_list = [
            {
                "id": str(e.id) if hasattr(e, "id") else str(uuid4()),
                "event_type": e.event_type if hasattr(e, "event_type") else "TimelineEvent",
                "message": e.message if hasattr(e, "message") else (e.details if hasattr(e, "details") else str(e)),
                "occurred_at": e.occurred_at.isoformat() if hasattr(e, "occurred_at") and e.occurred_at else None,
            }
            for e in events
        ]

        # 5. Fetch operational state (zones status & telemetry metrics)
        states = await self.state_manager.state_repo.list()
        avg_density = sum(s.density.value for s in states) / len(states) if states else 0.0
        avg_queue_wait = sum(s.queue_estimate.waiting_minutes for s in states) / len(states) if states else 0.0

        telemetry_data = {
            "average_crowd_density": avg_density,
            "average_queue_wait_minutes": avg_queue_wait,
            "zones_count": len(states),
            "stadium_health": snapshot.stadium_health,
            "zone_details": [
                {
                    "zone_id": str(s.zone_id),
                    "density": s.density.value,
                    "queue_waiting_minutes": s.queue_estimate.waiting_minutes,
                }
                for s in states
            ],
        }

        # 6. Formatting history
        history_lines = []
        for msg in request.history:
            history_lines.append(f"{msg.role.upper()}: {msg.text}")
        history_str = "\n".join(history_lines) if history_lines else "No history."

        # 7. Execute AI Orchestrator with complete memory context
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=CopilotChatResponse,
            message=request.message,
            language=request.language,
            history=history_str,
            current_page=request.current_page or "Mission Control (Home)",
            telemetry_context=json.dumps(telemetry_data, indent=2, default=str),
            incidents=json.dumps(incidents_data, indent=2, default=str),
            operator_decisions=json.dumps(operator_decisions, indent=2, default=str),
            recent_recommendations=json.dumps(recent_recommendations, indent=2, default=str),
            timeline=json.dumps(timeline_list, indent=2, default=str),
            min_confidence=0.0,
        )

        end_time = time.perf_counter()
        execution_time_ms = int((end_time - start_time) * 1000)

        # Enforce execution time and model version on the structured response
        report.execution_time_ms = execution_time_ms
        report.model_version = "Gemini 2.5 Flash"

        return report
