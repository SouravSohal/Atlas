from typing import Any

from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.enums.recommendation_status import RecommendationStatus
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository
from atlas_core.domain.repositories.task_repository import TaskRepository
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.application.operational_state.state_manager import OperationalStateManager
from app.application.recommendations import (
    AIRecommendationGenerator,
    RecommendationAgent,
    RecommendationAgentResponse,
)
from app.dependencies.container import ApplicationContainer
from app.infrastructure.security.rate_limiter import RateLimiterDependency
from app.presentation.responses import ApiResponse

from .models import (
    RecommendationDashboardItem,
    RecommendationDashboardListResponse,
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
        # Transform objects to expected dict representations
        operational_state_summary = {
            "stadium_health": snapshot.stadium_health,
            "timestamp": snapshot.timestamp.isoformat(),
            "zones_count": len(snapshot.crowd_conditions),
        }
        incidents_data = [
            {
                "id": str(inc.id),
                "incident_type": inc.incident_type,
                "severity": inc.severity,
                "description": inc.description,
            }
            for inc in active_incidents
        ]
        recs_data = [
            {
                "id": str(r.id),
                "action_type": r.action_type,
                "priority": r.priority,
                "details": r.details,
            }
            for r in active_recs
        ]
        explanation = await rec_agent.analyze_recommendations(
            operational_state_summary=operational_state_summary,
            incidents=incidents_data,
            business_recommendations=recs_data,
        )
        return ApiResponse(success=True, data=explanation)
    except Exception:
        fallback = RecommendationAgentResponse(
            natural_language_explanation="Explainability services are offline. Prioritizing routing guidelines based on default stadium safety protocol rules.",
            risk_assessment="Stadium capacity limit checks and zone queuing limits. Queue length estimates and zone incident counts.",
            prioritized_recommendations=[],
            alternative_actions=["Deploy auxiliary guides if ingress surges"],
            confidence_score=0.9,
            rationale="Fallback default rules applied due to offline explainability services.",
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
        # Transform objects to expected dict/list representations
        telemetry = {
            "crowd_density": snapshot.crowd_conditions,
            "wait_times": snapshot.queue_information,
        }
        incidents_data = [
            {
                "id": str(inc.id),
                "incident_type": inc.incident_type,
                "severity": inc.severity,
                "description": inc.description,
            }
            for inc in active_incidents
        ]
        operational_state = {
            "stadium_health": snapshot.stadium_health,
        }

        response = await generator.generate_recommendations(
            telemetry=telemetry,
            incidents=incidents_data,
            operational_state=operational_state,
        )

        saved_items = []
        for item in response.recommendations:
            rec = Recommendation(
                action_type=item.action_type,
                priority=Severity(item.priority.lower()),
                confidence=ConfidenceScore(value=item.confidence),
                details=item.explanation,
                status=RecommendationStatus.PENDING,
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
        return ApiResponse(success=False, error=f"Recommendation generation failed: {e!s}")
