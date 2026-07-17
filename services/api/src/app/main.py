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
from app.presentation.routers.dashboard import router as dashboard_router
from app.presentation.routers.health import router as health_router
from app.presentation.routers.incidents import router as incidents_router
from app.presentation.routers.version import router as version_router
from app.presentation.routers.copilot import router as copilot_router
from app.presentation.routers.streaming import router as streaming_router
from app.presentation.routers.demo_engine import router as demo_router
from app.presentation.routers.auth import router as auth_router

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

    # Seed Demo User if demo mode is enabled or app is in development env
    if settings.demo.mode or settings.app.environment == Environment.DEVELOPMENT:
        try:
            import uuid
            from datetime import datetime, UTC
            from atlas_core.domain.enums.user_role import UserRole
            from firebase_admin import auth

            demo_email = settings.demo.email.strip().lower()
            demo_password = settings.demo.password
            role_str = settings.demo.role.lower().replace(" ", "_")
            try:
                demo_role = UserRole(role_str)
            except ValueError:
                demo_role = UserRole.ADMINISTRATOR

            # 1. Sync user inside Firebase Authentication
            try:
                firebase_user = auth.get_user_by_email(demo_email)
                # Update password to stay in sync with configuration env variables
                auth.update_user(firebase_user.uid, password=demo_password)
            except Exception:
                # UserNotFoundError or other error: Create the user
                firebase_user = auth.create_user(
                    email=demo_email,
                    password=demo_password,
                    display_name="ATLAS Demo User",
                )
                logger.info("Successfully seeded demo user in Firebase Authentication", email=demo_email)
        except Exception as e:
            logger.error("Lifespan: Failed to seed Firebase demo user", error=str(e))

    logger.info(
        "ATLAS API service startup complete",
        app_name=settings.app.name,
        environment=settings.app.environment,
        version=settings.app.version,
    )

    yield

    # Shutdown
    logger.info("Shutting down API backend service")
    try:
        await container.firestore_client().close()
    except Exception as e:
        logger.warning("Failed to close firestore client during shutdown", error=str(e))
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
    app.include_router(dashboard_router)
    app.include_router(copilot_router)
    app.include_router(streaming_router)
    app.include_router(demo_router)
    app.include_router(auth_router)

    return app

app = create_app()
