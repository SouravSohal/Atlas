from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.config.settings import Settings
from app.dependencies.container import Container
from app.presentation.health import router as health_router
from app.presentation.version import router as version_router
from app.shared.logging import configure_logging

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifespan events."""
    logger.info("Starting up API backend service")
    yield
    logger.info("Shutting down API backend service")

def create_app() -> FastAPI:
    """Application factory for the FastAPI backend service."""
    container = Container()

    settings: Settings = container.config()
    configure_logging(settings.environment)

    app = FastAPI(
        title=settings.app_name,
        description="Modular Monolith API Gateway and Orchestrator for the ATLAS Stadium Intelligence System.",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.state.container = container

    app.include_router(health_router)
    app.include_router(version_router)

    return app

app = create_app()
