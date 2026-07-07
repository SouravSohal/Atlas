import structlog
from dependency_injector import containers, providers

from app.application.events import EventDispatcher, EventPublisher, EventRegistry, InMemoryEventBus
from app.config import get_settings
from app.infrastructure.auth import FirebaseAuthProvider


class ApplicationContainer(containers.DeclarativeContainer):
    """Core dependency injection container for the ATLAS backend service."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.presentation.routers.health",
            "app.presentation.routers.version",
            "app.dependencies.auth",
            "app.main",
        ]
    )

    # Core Providers
    config = providers.Callable(get_settings)
    logger = providers.Singleton(structlog.get_logger)
    auth_provider = providers.Singleton(FirebaseAuthProvider, settings=config)

    # Event Bus Framework
    event_registry = providers.Singleton(EventRegistry)
    event_dispatcher = providers.Singleton(EventDispatcher, registry=event_registry)
    event_bus = providers.Singleton(InMemoryEventBus, dispatcher=event_dispatcher)
    event_publisher = providers.Singleton(EventPublisher, event_bus=event_bus)

    # Future Infrastructure/Service Providers (Placeholders for future milestones)
    firestore_client = providers.Singleton(lambda: None)
    gemini_client = providers.Singleton(lambda: None)
    firebase_app = providers.Singleton(lambda: None)
    maps_client = providers.Singleton(lambda: None)
