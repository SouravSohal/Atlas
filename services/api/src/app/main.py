from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import Environment, Settings, configure_logging, get_settings
from app.dependencies import ApplicationContainer
from app.presentation.exception_handlers import register_exception_handlers
from app.presentation.middleware import RequestIdMiddleware, SecurityHeadersMiddleware
from app.presentation.routers.health import router as health_router
from app.presentation.routers.incidents import router as incidents_router
from app.presentation.routers.version import router as version_router

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifespan events."""
    # Startup
    settings: Settings = get_settings()

    # Validate Environment
    if settings.app.environment not in list(Environment):
        raise ValueError(f"Invalid environment value: {settings.app.environment}")

    # Initialize Logger
    configure_logging(settings)

    # Initialize Container Resources
    container: ApplicationContainer = app.state.container
    container.init_resources()

    logger.info(
        "ATLAS API service startup complete",
        app_name=settings.app.name,
        environment=settings.app.environment,
        version=settings.app.version,
    )

    yield

    # Shutdown
    logger.info("Shutting down API backend service")
    container.shutdown_resources()

def create_app() -> FastAPI:
    """Application factory for the FastAPI backend service."""
    container = ApplicationContainer()

    settings: Settings = container.config()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app.name,
        description="Modular Monolith API Gateway and Orchestrator for the ATLAS Stadium Intelligence System.",
        version=settings.app.version,
        lifespan=lifespan,
    )

    app.state.container = container

    # Register Middlewares (Request ID should wrap all, followed by security headers, gzip, and CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Register Global Exception Handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(health_router)
    app.include_router(version_router)
    app.include_router(incidents_router)

    return app

app = create_app()
