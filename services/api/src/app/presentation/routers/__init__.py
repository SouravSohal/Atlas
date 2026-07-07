from app.presentation.routers.health import router as health_router
from app.presentation.routers.version import router as version_router
from app.presentation.routers.incidents import router as incidents_router

__all__ = ["health_router", "version_router", "incidents_router"]
