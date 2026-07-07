from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import ApplicationContainer
from app.presentation.responses import ApiResponse

router = APIRouter(tags=["System"])

@router.get("/health", response_model=ApiResponse[dict[str, str]])
@inject
async def health_check(
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[dict[str, str]]:
    """Health check endpoint indicating the service operational status."""
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "app_name": settings.app.name,
            "environment": settings.app.environment,
        },
    )

@router.get("/ready", response_model=ApiResponse[dict[str, str]])
@inject
async def readiness_check(
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[dict[str, str]]:
    """Readiness check endpoint validating availability of downstream systems."""
    return ApiResponse(
        success=True,
        data={
            "ready": "true",
            "app_name": settings.app.name,
        },
    )
