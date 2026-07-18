from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import ApplicationContainer
from app.dependencies.auth import get_current_user
from app.presentation.responses import ApiResponse

router = APIRouter(tags=["System"], dependencies=[Depends(get_current_user)])

@router.get("/version", response_model=ApiResponse[dict[str, str]])
@inject
async def get_version(
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[dict[str, str]]:
    """Version check endpoint returning current release metadata."""
    return ApiResponse(
        success=True,
        data={
            "version": settings.app.version,
            "environment": settings.app.environment,
        },
    )
