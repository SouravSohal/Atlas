from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import ApplicationContainer

router = APIRouter(tags=["System"])

@router.get("/version")
@inject
async def get_version(
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> dict[str, str]:
    """Version check endpoint returning current release metadata."""
    return {
        "version": settings.app.version,
        "environment": settings.app.environment,
    }
