from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.incidents import (
    CreateIncidentRequest,
    CreateIncidentUseCase,
    GetIncidentUseCase,
    IncidentResponse,
    ListIncidentsUseCase,
    UpdateIncidentRequest,
    UpdateIncidentUseCase,
)
from app.dependencies.auth import require_staff
from app.dependencies.container import ApplicationContainer
from app.infrastructure.cache.manager import cache_manager
from app.presentation.responses import ApiResponse

router = APIRouter(prefix="/incidents", tags=["Incidents"], dependencies=[Depends(require_staff)])

@router.post("", response_model=ApiResponse[IncidentResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_incident(
    request: CreateIncidentRequest,
    use_case: CreateIncidentUseCase = Depends(Provide[ApplicationContainer.create_incident_use_case]),
) -> ApiResponse[IncidentResponse]:
    """Report and create a new incident in the system."""
    try:
        response_dto = await use_case.execute(request)
        await cache_manager.invalidate_prefix("dashboard:")
        return ApiResponse(success=True, data=response_dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

@router.get("/{id}", response_model=ApiResponse[IncidentResponse])
@inject
async def get_incident(
    id: UUID,
    use_case: GetIncidentUseCase = Depends(Provide[ApplicationContainer.get_incident_use_case]),
) -> ApiResponse[IncidentResponse]:
    """Retrieve an incident by its unique ID."""
    response_dto = await use_case.execute(id)
    if not response_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {id} not found.",
        )
    return ApiResponse(success=True, data=response_dto)

@router.get("", response_model=ApiResponse[list[IncidentResponse]])
@inject
async def list_incidents(
    use_case: ListIncidentsUseCase = Depends(Provide[ApplicationContainer.list_incidents_use_case]),
) -> ApiResponse[list[IncidentResponse]]:
    """List all incidents recorded in the system."""
    response_dtos = await use_case.execute()
    return ApiResponse(success=True, data=list(response_dtos))

@router.patch("/{id}", response_model=ApiResponse[IncidentResponse])
@inject
async def update_incident(
    id: UUID,
    request: UpdateIncidentRequest,
    use_case: UpdateIncidentUseCase = Depends(Provide[ApplicationContainer.update_incident_use_case]),
) -> ApiResponse[IncidentResponse]:
    """Update or resolve an incident in the system."""
    response_dto = await use_case.execute(id, request)
    if not response_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {id} not found.",
        )
    await cache_manager.invalidate_prefix("dashboard:")
    return ApiResponse(success=True, data=response_dto)
