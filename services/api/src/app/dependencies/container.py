import structlog
from dependency_injector import containers, providers

from app.config import get_settings


class ApplicationContainer(containers.DeclarativeContainer):
    """Core dependency injection container for the ATLAS backend service."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.presentation.routers.health",
            "app.presentation.routers.version",
            "app.main",
        ]
    )

    # Core Providers
    config = providers.Callable(get_settings)
    logger = providers.Singleton(structlog.get_logger)

    # Future Infrastructure/Service Providers (Placeholders for future milestones)
    firestore_client = providers.Singleton(lambda: None)
    gemini_client = providers.Singleton(lambda: None)
    firebase_app = providers.Singleton(lambda: None)
    maps_client = providers.Singleton(lambda: None)
