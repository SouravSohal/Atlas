from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.dependencies.container import ApplicationContainer
from app.presentation.responses import ApiResponse

from .models import (
    IncidentDashboardItem,
    IncidentDashboardListResponse,
)

router = APIRouter()

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
    paginated, total_count = await incident_repo.list_paginated(
        page=page,
        limit=limit,
        resolved=resolved,
        severity=severity,
        incident_type=incident_type,
        sort_by=sort_by,
        order=order,
    )

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
