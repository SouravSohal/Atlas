from typing import Any
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject

from app.dependencies.container import ApplicationContainer
from app.presentation.responses import ApiResponse
from app.infrastructure.security.rate_limiter import RateLimiterDependency

from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.task_repository import TaskRepository
from app.application.operational_state.state_manager import OperationalStateManager

from app.application.recommendations import (
    RecommendationAgent,
    RecommendationAgentResponse,
    AIRecommendationGenerator,
)

from .models import (
    RecommendationDashboardListResponse,
    RecommendationDashboardItem,
)

router = APIRouter()

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
    paginated, total_count = await recommendation_repo.list_paginated(
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        action_type=action_type,
        sort_by=sort_by,
        order=order,
    )

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


@router.get("/recommendations/explain", response_model=ApiResponse[RecommendationAgentResponse], dependencies=[Depends(RateLimiterDependency("ai"))])
@inject
async def explain_recommendations(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: Any = Depends(Provide[ApplicationContainer.event_publisher]),
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

    try:
        explanation = await rec_agent.explain_recommendations(
            snapshot=snapshot,
            active_incidents=active_incidents,
            recommendations=active_recs,
        )
        return ApiResponse(success=True, data=explanation)
    except Exception as e:
        fallback = RecommendationAgentResponse(
            justification="Explainability services are offline. Prioritizing routing guidelines based on default stadium safety protocol rules.",
            evidence="Stadium capacity limit checks and zone queuing limits.",
            operational_data_used="Queue length estimates and zone incident counts.",
            confidence_score=0.9,
            prioritized_recommendations=[],
            alternative_strategies=["Deploy auxiliary guides if ingress surges"],
        )
        return ApiResponse(success=True, data=fallback)


@router.post("/recommendations/generate", response_model=ApiResponse[list[RecommendationDashboardItem]], dependencies=[Depends(RateLimiterDependency("ai"))])
@inject
async def generate_ai_recommendations(
    state_repo: OperationalStateRepository[OperationalState] = Depends(Provide[ApplicationContainer.operational_state_repository]),
    incident_repo: IncidentRepository[Incident] = Depends(Provide[ApplicationContainer.incident_repository]),
    task_repo: TaskRepository[Any] = Depends(Provide[ApplicationContainer.task_repository]),
    recommendation_repo: RecommendationRepository[Recommendation] = Depends(Provide[ApplicationContainer.recommendation_repository]),
    event_publisher: Any = Depends(Provide[ApplicationContainer.event_publisher]),
    generator: AIRecommendationGenerator = Depends(Provide[ApplicationContainer.recommendation_generator]),
) -> ApiResponse[list[RecommendationDashboardItem]]:
    """Triggers the AI Generator to analyze active stadium state and append fresh recommendations."""
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
        new_recs = await generator.generate_recommendations(
            snapshot=snapshot,
            active_incidents=active_incidents,
        )

        saved_items = []
        for rec in new_recs:
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
        return ApiResponse(success=False, error={"code": "AI_ERROR", "message": f"Recommendation generation failed: {str(e)}"})
