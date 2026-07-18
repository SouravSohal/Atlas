from fastapi import APIRouter, Depends

from app.dependencies.auth import require_staff

from .ai import router as ai_router
from .incidents import router as incidents_router
from .overview import router as overview_router
from .recommendations import router as recommendations_router

router = APIRouter(prefix="/dashboard", tags=["Operations Command Center"], dependencies=[Depends(require_staff)])

router.include_router(overview_router)
router.include_router(incidents_router)
router.include_router(recommendations_router)
router.include_router(ai_router)
