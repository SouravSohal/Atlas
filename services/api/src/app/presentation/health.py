from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies.container import Container

router = APIRouter(tags=["System"])

@router.get("/health")
@inject
async def health_check(
    settings: Settings = Depends(Provide[Container.config]),
) -> dict[str, str]:
    """Health check endpoint indicating the service operational status."""
    return {
        "status": "healthy",
        "app_name": settings.app.name,
        "environment": settings.app.environment,
    }
