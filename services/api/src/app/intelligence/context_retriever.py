from typing import Any
from uuid import UUID


class ContextRetriever:
    """Retrieves operational data from repositories and builds structured context summaries."""

    def __init__(
        self,
        state_repository: Any,
        incident_repository: Any,
        recommendation_repository: Any,
    ) -> None:
        self.state_repository = state_repository
        self.incident_repository = incident_repository
        self.recommendation_repository = recommendation_repository

    async def retrieve_zone_context(self, zone_id: UUID) -> dict[str, Any]:
        """Compiles a complete context package for a specific zone."""
        state = await self.state_repository.get_by_id(zone_id)
        state_info = {
            "zone_id": str(zone_id),
            "density": state.density.value if state else 0.0,
            "queue_waiting_minutes": state.queue_estimate.waiting_minutes if state else 0,
        }

        incidents = await self.incident_repository.list()
        incident_summary = [
            {
                "id": str(inc.id),
                "type": inc.incident_type.value,
                "severity": inc.severity.value,
                "description": inc.description,
                "resolved": inc.resolved,
            }
            for inc in incidents
        ]

        recs = await self.recommendation_repository.list()
        rec_summary = [
            {
                "id": str(rec.id),
                "action_type": rec.action_type,
                "priority": rec.priority.value,
                "status": rec.status.value,
            }
            for rec in recs
        ]

        return {
            "operational_state": state_info,
            "incidents": incident_summary,
            "recommendations": rec_summary,
        }
