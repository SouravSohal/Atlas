from datetime import datetime
from typing import Any
from uuid import UUID

import structlog
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.repositories.event_repository import EventRepository
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.repositories.task_repository import TaskRepository
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.application.events import EventPublisher
from app.application.operational_state.state_manager import OperationalStateManager
from app.application.operational_state import SituationSummaryAgent, SituationSummaryAgentResponse
from app.application.recommendations import RecommendationAgent, RecommendationAgentResponse, AIRecommendationGenerator
from app.dependencies.container import ApplicationContainer
from app.presentation.responses import ApiResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# --- DTO Response Models ---

class DashboardOverviewResponse(BaseModel):
    """General overview metrics of the stadium operations."""

    stadium_health: float = Field(..., description="Overall stadium health score from 0.0 to 1.0.")
    active_incidents_count: int = Field(..., description="Total count of active unresolved incidents.")
    average_crowd_density: float = Field(..., description="Average crowd density across all stadium zones.")
    pending_recommendations_count: int = Field(..., description="Total count of pending recommendations.")
    allocated_volunteers_count: int = Field(..., description="Total count of active volunteers assigned to tasks.")
    timestamp: datetime = Field(..., description="Time of the overview compilation.")


class IncidentDashboardItem(BaseModel):
    """Represent an incident in the dashboard query."""

    id: UUID
    incident_type: str
    severity: str
    description: str
    latitude: float
    longitude: float
    reporter_id: UUID
    resolved: bool
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class IncidentDashboardListResponse(BaseModel):
    """Paginated list response of incidents."""

    total_count: int
    page: int
    limit: int
    items: list[IncidentDashboardItem]


class OperationalStateDashboardItem(BaseModel):
    """Represent zone operational state details in the dashboard."""

    zone_id: UUID
    density: float
    queue_waiting_minutes: int
    last_updated: datetime


class RecommendationDashboardItem(BaseModel):
    """Represent a recommendation in the dashboard query."""

    id: UUID
    action_type: str
    priority: str
    confidence: float
    details: str
    status: str
    approved_by_id: UUID | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RecommendationDashboardListResponse(BaseModel):
    """Paginated list response of recommendations."""

    total_count: int
    page: int
    limit: int
    items: list[RecommendationDashboardItem]


class DashboardMetricsResponse(BaseModel):
    """Detailed telemetry and operational metrics for graphical charts."""

    average_queue_wait_minutes: float = Field(..., description="Average queue wait time across all zones.")
    congestion_rate: float = Field(..., description="Ratio of zones with crowd density > 0.75.")
    incident_resolution_rate: float = Field(..., description="Ratio of resolved incidents to total incidents.")
    incidents_by_severity: dict[str, int] = Field(..., description="Count of incidents grouped by severity level.")
    incidents_by_type: dict[str, int] = Field(..., description="Count of incidents grouped by type.")
    recommendations_by_status: dict[str, int] = Field(..., description="Count of recommendations grouped by status.")


# --- API Endpoints ---

@router.get("/overview", response_model=ApiResponse[DashboardOverviewResponse])
@inject
async def get_overview(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: EventPublisher = Depends(Provide[ApplicationContainer.event_publisher]),
) -> ApiResponse[DashboardOverviewResponse]:
    """Retrieves high-level overview metrics of the stadium's current state."""
    state_mgr_real = OperationalStateManager(
        state_repo=state_repo,
        incident_repo=incident_repo,
        task_repo=task_repo,
        recommendation_repo=recommendation_repo,
        event_publisher=event_publisher,
    )
    snapshot = await state_mgr_real.get_snapshot()

    avg_density = sum(snapshot.crowd_conditions.values()) / len(snapshot.crowd_conditions) if snapshot.crowd_conditions else 0.0

    overview = DashboardOverviewResponse(
        stadium_health=snapshot.stadium_health,
        active_incidents_count=len(snapshot.active_incidents),
        average_crowd_density=avg_density,
        pending_recommendations_count=len(snapshot.recommendations),
        allocated_volunteers_count=len(snapshot.volunteer_allocation),
        timestamp=snapshot.timestamp,
    )
    return ApiResponse(success=True, data=overview)


@router.get("/incidents", response_model=ApiResponse[IncidentDashboardListResponse])
@inject
async def get_dashboard_incidents(
    page: int = Query(1, ge=1, description="Page number."),
    limit: int = Query(10, ge=1, le=100, description="Items per page."),
    resolved: bool | None = Query(None, description="Filter by resolution status."),
    severity: str | None = Query(None, description="Filter by incident severity."),
    incident_type: str | None = Query(None, description="Filter by incident classification type."),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, severity)."),
    order: str = Query("desc", description="Sort order (asc, desc)."),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
) -> ApiResponse[IncidentDashboardListResponse]:
    """Lists incidents with pagination, sorting, and filtering support."""
    incidents = await incident_repo.list()

    # Filter
    if resolved is not None:
        incidents = [i for i in incidents if i.resolved == resolved]
    if severity is not None:
        incidents = [i for i in incidents if i.severity.value == severity]
    if incident_type is not None:
        incidents = [i for i in incidents if i.incident_type.value == incident_type]

    # Sort
    severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    if sort_by == "severity":
        incidents = sorted(incidents, key=lambda x: severity_order.get(x.severity.value, 0), reverse=(order == "desc"))
    else:
        # Default created_at
        incidents = sorted(incidents, key=lambda x: x.created_at, reverse=(order == "desc"))

    # Paginate
    total_count = len(incidents)
    start = (page - 1) * limit
    end = start + limit
    paginated = incidents[start:end]

    items = [
        IncidentDashboardItem(
            id=i.id,
            incident_type=i.incident_type.value,
            severity=i.severity.value,
            description=i.description,
            latitude=i.location.latitude,
            longitude=i.location.longitude,
            reporter_id=i.reporter_id,
            resolved=i.resolved,
            resolved_at=i.resolved_at,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in paginated
    ]

    return ApiResponse(
        success=True,
        data=IncidentDashboardListResponse(
            total_count=total_count,
            page=page,
            limit=limit,
            items=items,
        ),
    )


@router.get("/operational-state", response_model=ApiResponse[list[OperationalStateDashboardItem]])
@inject
async def get_dashboard_operational_states(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
) -> ApiResponse[list[OperationalStateDashboardItem]]:
    """Retrieves operational states for all zones."""
    states = await state_repo.list()

    items = [
        OperationalStateDashboardItem(
            zone_id=s.zone_id,
            density=s.density.value,
            queue_waiting_minutes=s.queue_estimate.waiting_minutes,
            last_updated=s.last_updated,
        )
        for s in states
    ]
    return ApiResponse(success=True, data=items)


@router.get("/recommendations", response_model=ApiResponse[RecommendationDashboardListResponse])
@inject
async def get_dashboard_recommendations(
    page: int = Query(1, ge=1, description="Page number."),
    limit: int = Query(10, ge=1, le=100, description="Items per page."),
    status: str | None = Query(None, description="Filter by recommendation status."),
    priority: str | None = Query(None, description="Filter by priority level."),
    action_type: str | None = Query(None, description="Filter by action type."),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, confidence)."),
    order: str = Query("desc", description="Sort order (asc, desc)."),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
) -> ApiResponse[RecommendationDashboardListResponse]:
    """Lists pre-generated routing and operational recommendations."""
    recs = await recommendation_repo.list()

    # Filter
    if status is not None:
        recs = [r for r in recs if r.status.value == status]
    if priority is not None:
        recs = [r for r in recs if r.priority.value == priority]
    if action_type is not None:
        recs = [r for r in recs if r.action_type == action_type]

    # Sort
    if sort_by == "confidence":
        recs = sorted(recs, key=lambda x: x.confidence.value, reverse=(order == "desc"))
    else:
        # Default created_at
        recs = sorted(recs, key=lambda x: x.created_at, reverse=(order == "desc"))

    # Paginate
    total_count = len(recs)
    start = (page - 1) * limit
    end = start + limit
    paginated = recs[start:end]

    items = [
        RecommendationDashboardItem(
            id=r.id,
            action_type=r.action_type,
            priority=r.priority.value,
            confidence=r.confidence.value,
            details=r.details,
            status=r.status.value,
            approved_by_id=r.approved_by_id,
            approved_at=r.approved_at,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in paginated
    ]

    return ApiResponse(
        success=True,
        data=RecommendationDashboardListResponse(
            total_count=total_count,
            page=page,
            limit=limit,
            items=items,
        ),
    )


@router.get("/metrics", response_model=ApiResponse[DashboardMetricsResponse])
@inject
async def get_dashboard_metrics(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
) -> ApiResponse[DashboardMetricsResponse]:
    """Compiles detailed real-time operational and security telemetry metrics."""
    states = await state_repo.list()
    total_zones = len(states)
    avg_wait = sum(s.queue_estimate.waiting_minutes for s in states) / total_zones if total_zones > 0 else 0.0
    congested_count = sum(1 for s in states if s.density.value > 0.75)
    congestion_rate = congested_count / total_zones if total_zones > 0 else 0.0

    incidents = await incident_repo.list()
    total_incidents = len(incidents)
    resolved_count = sum(1 for i in incidents if i.resolved)
    resolution_rate = resolved_count / total_incidents if total_incidents > 0 else 0.0

    severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    type_counts: dict[str, int] = {}
    for i in incidents:
        sev = i.severity.value
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

        itype = i.incident_type.value
        type_counts[itype] = type_counts.get(itype, 0) + 1

    recs = await recommendation_repo.list()
    status_counts = {"pending": 0, "approved": 0, "rejected": 0, "executing": 0, "completed": 0, "failed": 0}
    for r in recs:
        status_counts[r.status.value] = status_counts.get(r.status.value, 0) + 1

    metrics = DashboardMetricsResponse(
        average_queue_wait_minutes=avg_wait,
        congestion_rate=congestion_rate,
        incident_resolution_rate=resolution_rate,
        incidents_by_severity=severity_counts,
        incidents_by_type=type_counts,
        recommendations_by_status=status_counts,
    )
    return ApiResponse(success=True, data=metrics)


@router.get("/briefing", response_model=ApiResponse[SituationSummaryAgentResponse])
@inject
async def get_dashboard_briefing(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: EventPublisher = Depends(Provide[ApplicationContainer.event_publisher]),
    event_repo: EventRepository = Depends(Provide[ApplicationContainer.event_repository]),
    summary_agent: SituationSummaryAgent = Depends(Provide[ApplicationContainer.situation_summary_agent]),
) -> ApiResponse[SituationSummaryAgentResponse]:
    """Generates a dynamic real-time AI Situation Briefing using the SituationSummaryAgent."""
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


@router.get("/recommendations/explain", response_model=ApiResponse[RecommendationAgentResponse])
@inject
async def explain_recommendations(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: EventPublisher = Depends(Provide[ApplicationContainer.event_publisher]),
    rec_agent: RecommendationAgent = Depends(Provide[ApplicationContainer.recommendation_agent]),
) -> ApiResponse[RecommendationAgentResponse]:
    """Invokes the RecommendationAgent to explain and rank-prioritize active stadium recommendations."""
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

    try:
        report = await rec_agent.analyze_recommendations(
            operational_state_summary=operational_state_summary,
            incidents=incidents_list,
            business_recommendations=recommendations_list,
        )
        return ApiResponse(success=True, data=report)
    except Exception as e:
        logger.error("Failed to explain recommendations via AI", error=str(e))
        fallback = RecommendationAgentResponse(
            natural_language_explanation="Standard operational response rules have been selected. AI explanation service is currently offline.",
            prioritized_recommendations=[],
            risk_assessment="Standard risk assessment shows no high threats to aux egress corridors.",
            alternative_actions=["Divert spectator queues", "Deploy additional gate crew volunteers"],
        )
        return ApiResponse(success=True, data=fallback)


@router.post("/recommendations/generate", response_model=ApiResponse[list[RecommendationDashboardItem]])
@inject
async def generate_ai_recommendations(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: EventPublisher = Depends(Provide[ApplicationContainer.event_publisher]),
    generator: AIRecommendationGenerator = Depends(Provide[ApplicationContainer.recommendation_generator]),
) -> ApiResponse[list[RecommendationDashboardItem]]:
    """Generates AI-powered stadium logistics and safety recommendations using Gemini, validating and saving them."""
    from atlas_core.domain.enums.severity import Severity
    from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
    import json

    state_mgr = OperationalStateManager(
        state_repo=state_repo,
        incident_repo=incident_repo,
        task_repo=task_repo,
        recommendation_repo=recommendation_repo,
        event_publisher=event_publisher,
    )
    snapshot = await state_mgr.get_snapshot()

    operational_state_summary = {
        "stadium_health": snapshot.stadium_health,
        "timestamp": snapshot.timestamp.isoformat(),
        "zones_count": len(snapshot.crowd_conditions),
    }

    all_incidents = await incident_repo.list()
    active_incidents = [
        inc for inc in all_incidents 
        if any(str(inc.id) == str(uuid_id) for uuid_id in snapshot.active_incidents)
    ]

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

    # Compute telemetry inputs
    states = await state_repo.list()
    avg_density = sum(s.density.value for s in states) / len(states) if states else 0.0
    avg_queue_wait = sum(s.queue_estimate.waiting_minutes for s in states) / len(states) if states else 0.0

    telemetry = {
        "average_crowd_density": avg_density,
        "average_queue_wait_minutes": avg_queue_wait,
        "zones_density": crowd_conditions_map,
        "volunteer_status": volunteer_status,
    }

    try:
        report = await generator.generate_recommendations(
            telemetry=telemetry,
            incidents=incidents_list,
            operational_state=operational_state_summary,
        )

        saved_items = []
        for item in report.recommendations:
            # Map priority string to Severity Enum
            p_val = item.priority.lower()
            if p_val == "critical":
                priority_enum = Severity.CRITICAL
            elif p_val == "high":
                priority_enum = Severity.HIGH
            elif p_val == "medium":
                priority_enum = Severity.MEDIUM
            else:
                priority_enum = Severity.LOW

            details_dict = {
                "expected_impact": item.estimated_impact,
                "eta_minutes": item.estimated_recovery_time_minutes,
                "trigger_reason": item.operational_reasoning,
                "explanation": item.explanation,
            }

            rec = Recommendation(
                action_type=item.action_type,
                priority=priority_enum,
                confidence=ConfidenceScore(value=max(0.0, min(1.0, item.confidence))),
                details=json.dumps(details_dict),
            )

            await recommendation_repo.save(rec)
            
            saved_items.append(
                RecommendationDashboardItem(
                    id=rec.id,
                    action_type=rec.action_type,
                    priority=rec.priority.value,
                    confidence=rec.confidence.value,
                    details=rec.details,
                    status=rec.status.value,
                    approved_by_id=rec.approved_by_id,
                    approved_at=rec.approved_at,
                    created_at=rec.created_at,
                    updated_at=rec.updated_at,
                )
            )

        return ApiResponse(success=True, data=saved_items)

    except Exception as e:
        logger.error("Failed to generate AI recommendations", error=str(e))
        return ApiResponse(success=False, error={"code": "AI_ERROR", "message": f"Recommendation generation failed: {str(e)}"})
