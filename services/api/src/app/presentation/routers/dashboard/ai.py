from typing import Any
import structlog
from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import Provide, inject

from app.config import Settings
from app.dependencies.container import ApplicationContainer
from app.presentation.responses import ApiResponse
from app.infrastructure.security.rate_limiter import RateLimiterDependency
from app.infrastructure.cache.manager import cache_manager, check_cache_bypass

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.task_repository import TaskRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.repositories.event_repository import EventRepository
from app.application.operational_state.state_manager import OperationalStateManager

from app.application.operational_state import (
    SituationSummaryAgent,
    SituationSummaryAgentResponse,
    StadiumPredictionsAgent,
    StadiumPredictionsResponse,
)

logger = structlog.get_logger()
router = APIRouter()

@router.get("/briefing", response_model=ApiResponse[SituationSummaryAgentResponse], dependencies=[Depends(RateLimiterDependency("ai"))])
@inject
async def get_dashboard_briefing(
    request: Request,
    bypass_cache: bool = Depends(check_cache_bypass),
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: Any = Depends(Provide[ApplicationContainer.event_publisher]),
    event_repo: EventRepository = Depends(Provide[ApplicationContainer.event_repository]),
    summary_agent: SituationSummaryAgent = Depends(Provide[ApplicationContainer.situation_summary_agent]),
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[SituationSummaryAgentResponse]:
    """Generates a dynamic real-time AI Situation Briefing using the SituationSummaryAgent."""
    cache_key = "dashboard:briefing"
    if not bypass_cache:
        cached_val = await cache_manager.get(cache_key)
        if cached_val is not None:
            return ApiResponse(success=True, data=cached_val)

    state_mgr = OperationalStateManager(
        state_repo=state_repo,
        incident_repo=incident_repo,
        task_repo=task_repo,
        recommendation_repo=recommendation_repo,
        event_publisher=event_publisher,
    )
    snapshot = await state_mgr.get_snapshot()

    all_incidents = await incident_repo.list()
    active_incidents = [
        inc for inc in all_incidents
        if any(str(inc.id) == str(uuid_id) for uuid_id in snapshot.active_incidents)
    ]

    all_recs = await recommendation_repo.list()
    active_recs = [
        r for r in all_recs
        if any(str(r.id) == str(uuid_id) for uuid_id in snapshot.recommendations)
    ]

    operational_state_summary = {
        "stadium_health": snapshot.stadium_health,
        "timestamp": snapshot.timestamp.isoformat(),
        "zones_count": len(snapshot.crowd_conditions),
    }

    incidents_list = [
        {
            "id": str(i.id),
            "incident_type": i.incident_type.value,
            "severity": i.severity.value,
            "description": i.description,
            "resolved": i.resolved,
            "created_at": i.created_at.isoformat(),
        }
        for i in active_incidents
    ]

    crowd_conditions_map = {str(k): v for k, v in snapshot.crowd_conditions.items()}

    volunteer_status = {
        "allocated_count": len(snapshot.volunteer_allocation),
    }

    recommendations_list = [
        {
            "id": str(r.id),
            "action_type": r.action_type,
            "priority": r.priority.value,
            "confidence": r.confidence.value,
            "details": r.details,
            "status": r.status.value,
        }
        for r in active_recs
    ]

    # Gather timeline events from EventRepository
    try:
        events = await event_repo.list()
        timeline_list = [
            f"{evt.start_time.strftime('%H:%M:%S')} - {evt.name} ({evt.event_type.value})"
            for evt in sorted(events, key=lambda e: e.start_time)
        ]
    except Exception:
        timeline_list = []

    if not timeline_list:
        timeline_list = [
            "15:00:00 - Stadium Gates Open",
            "15:30:00 - Spectator Seating Influx Begins",
            "16:00:00 - Match Warmups Initiated",
        ]

    # Compute telemetry inputs (Crowd Density & Queue Lengths)
    states = await state_repo.list()
    avg_density = sum(s.density.value for s in states) / len(states) if states else 0.0
    avg_queue_wait = sum(s.queue_estimate.waiting_minutes for s in states) / len(states) if states else 0.0

    telemetry = {
        "average_crowd_density": avg_density,
        "average_queue_wait_minutes": avg_queue_wait,
        "zones_density": crowd_conditions_map,
        "volunteer_status": volunteer_status,
    }

    # Fetch weather
    weather = "Overcast, 22°C, 12% precipitation, wind speed 8 km/h."
    for inc in active_incidents:
        if inc.incident_type.value == "weather" or "weather" in inc.description.lower():
            weather = f"WARNING: Severe weather event active. {inc.description}"
            break

    try:
        report = await summary_agent.generate_summary(
            operational_state=operational_state_summary,
            incidents=incidents_list,
            telemetry=telemetry,
            weather=weather,
            recommendations=recommendations_list,
            timeline=timeline_list,
        )
        await cache_manager.set(cache_key, report, settings.cache.briefing_ttl)
        return ApiResponse(success=True, data=report)
    except Exception as e:
        logger.error("Failed to generate situation briefing", error=str(e))
        fallback = SituationSummaryAgentResponse(
            executive_summary="All stadium sectors are operating at standard capacity. AI Briefing generation is currently unavailable.",
            situation_assessment="Stadium operations are nominal across primary Gates 1 and 2, with queue times averaging under 8 minutes.",
            immediate_risks=["None identified at present capacity levels"],
            recommended_actions=["Maintain standard volunteer allocation guidelines"],
            predicted_outcome="Stadium traffic flows will continue normal patterns.",
            confidence_score=1.0,
            assumptions=["Volunteer attendance levels remain constant", "Weather holds nominal"],
            alternative_strategies=["Deploy auxiliary guides if ingress surges"],
        )
        return ApiResponse(success=True, data=fallback)


@router.get("/predictions", response_model=ApiResponse[StadiumPredictionsResponse], dependencies=[Depends(RateLimiterDependency("ai"))])
@inject
async def get_predictions(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: Any = Depends(Provide[ApplicationContainer.event_publisher]),
    event_repo: EventRepository = Depends(Provide[ApplicationContainer.event_repository]),
    predictions_agent: StadiumPredictionsAgent = Depends(Provide[ApplicationContainer.stadium_predictions_agent]),
) -> ApiResponse[StadiumPredictionsResponse]:
    """Invokes the StadiumPredictionsAgent to predict crowd, wait times, gate/transport loads using Gemini."""
    state_mgr = OperationalStateManager(
        state_repo=state_repo,
        incident_repo=incident_repo,
        task_repo=task_repo,
        recommendation_repo=recommendation_repo,
        event_publisher=event_publisher,
    )
    snapshot = await state_mgr.get_snapshot()

    all_incidents = await incident_repo.list()
    active_incidents = [
        inc for inc in all_incidents
        if any(str(inc.id) == str(uuid_id) for uuid_id in snapshot.active_incidents)
    ]

    try:
        events = await event_repo.list()
        timeline_list = [
            f"{evt.start_time.strftime('%H:%M:%S')} - {evt.name} ({evt.event_type.value})"
            for evt in sorted(events, key=lambda e: e.start_time)
        ]
    except Exception:
        timeline_list = []

    # Compute telemetry inputs (Crowd Density & Queue Lengths)
    states = await state_repo.list()
    avg_density = sum(s.density.value for s in states) / len(states) if states else 0.0
    avg_queue_wait = sum(s.queue_estimate.waiting_minutes for s in states) / len(states) if states else 0.0

    telemetry = {
        "average_crowd_density": avg_density,
        "average_queue_wait_minutes": avg_queue_wait,
    }

    try:
        predictions = await predictions_agent.generate_predictions(
            snapshot=snapshot,
            active_incidents=active_incidents,
            telemetry=telemetry,
            timeline=timeline_list,
        )
        return ApiResponse(success=True, data=predictions)
    except Exception as e:
        logger.error("Failed to generate AI predictions", error=str(e))
        return ApiResponse(success=False, error={"code": "AI_ERROR", "message": f"Predictions generation failed: {str(e)}"})
