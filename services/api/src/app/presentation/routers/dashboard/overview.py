from typing import Any

from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.repositories.task_repository import TaskRepository
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from app.application.events import EventPublisher
from app.application.operational_state.state_manager import OperationalStateManager
from app.config import Settings
from app.dependencies.container import ApplicationContainer
from app.infrastructure.cache.manager import cache_manager, check_cache_bypass
from app.presentation.responses import ApiResponse

from .models import (
    DashboardMetricsResponse,
    DashboardOverviewResponse,
    OperationalStateDashboardItem,
)

router = APIRouter()

@router.get("/overview", response_model=ApiResponse[DashboardOverviewResponse])
@inject
async def get_overview(
    request: Request,
    bypass_cache: bool = Depends(check_cache_bypass),
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: EventPublisher = Depends(Provide[ApplicationContainer.event_publisher]),
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[DashboardOverviewResponse]:
    """Retrieves high-level overview metrics of the stadium's current state."""
    cache_key = "dashboard:overview"
    if not bypass_cache:
        cached_val = await cache_manager.get(cache_key)
        if cached_val is not None:
            return ApiResponse(success=True, data=cached_val)

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
    await cache_manager.set(cache_key, overview, settings.cache.overview_ttl)
    return ApiResponse(success=True, data=overview)


@router.get("/operational-state", response_model=ApiResponse[list[OperationalStateDashboardItem]])
@inject
async def get_dashboard_operational_states(
    request: Request,
    bypass_cache: bool = Depends(check_cache_bypass),
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[list[OperationalStateDashboardItem]]:
    """Retrieves operational states for all zones."""
    cache_key = "dashboard:operational_state"
    if not bypass_cache:
        cached_val = await cache_manager.get(cache_key)
        if cached_val is not None:
            return ApiResponse(success=True, data=cached_val)

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
    await cache_manager.set(cache_key, items, settings.cache.operational_state_ttl)
    return ApiResponse(success=True, data=items)


@router.get("/metrics", response_model=ApiResponse[DashboardMetricsResponse])
@inject
async def get_dashboard_metrics(
    request: Request,
    bypass_cache: bool = Depends(check_cache_bypass),
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[DashboardMetricsResponse]:
    """Compiles detailed real-time operational and security telemetry metrics."""
    cache_key = "dashboard:metrics"
    if not bypass_cache:
        cached_val = await cache_manager.get(cache_key)
        if cached_val is not None:
            return ApiResponse(success=True, data=cached_val)

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
    await cache_manager.set(cache_key, metrics, settings.cache.metrics_ttl)
    return ApiResponse(success=True, data=metrics)
