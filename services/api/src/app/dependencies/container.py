import structlog
from dependency_injector import containers, providers

from app.application.events import EventDispatcher, EventPublisher, EventRegistry, InMemoryEventBus
from app.application.incidents import (
    CreateIncidentUseCase,
    GetIncidentUseCase,
    ListIncidentsUseCase,
    UpdateIncidentUseCase,
)
from app.application.operational_state import OperationalStateService
from app.config import get_settings
from app.infrastructure.auth import FirebaseAuthProvider
from app.infrastructure.firestore import FirestoreClient, FirestoreUnitOfWork, TransactionManager
from app.infrastructure.repositories import (
    FirestoreEventRepository,
    FirestoreIncidentRepository,
    FirestoreOperationalStateRepository,
    FirestoreRecommendationRepository,
    FirestoreTaskRepository,
)
from app.intelligence import AIOrchestrator, ModelGateway, PromptVersionManager


class ApplicationContainer(containers.DeclarativeContainer):
    """Core dependency injection container for the ATLAS backend service."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.presentation.routers.health",
            "app.presentation.routers.version",
            "app.presentation.routers.incidents",
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

    # Firestore Database Infrastructure
    firestore_client = providers.Singleton(FirestoreClient, settings=config)
    transaction_manager = providers.Singleton(TransactionManager, client=firestore_client)
    firestore_uow = providers.Factory(FirestoreUnitOfWork, client=firestore_client)

    # Repository Adapters
    event_repository = providers.Factory(FirestoreEventRepository, client=firestore_client)
    incident_repository = providers.Factory(FirestoreIncidentRepository, client=firestore_client)
    task_repository = providers.Factory(FirestoreTaskRepository, client=firestore_client)
    recommendation_repository = providers.Factory(FirestoreRecommendationRepository, client=firestore_client)
    operational_state_repository = providers.Factory(FirestoreOperationalStateRepository, client=firestore_client)

    # Application Services
    operational_state_service = providers.Factory(
        OperationalStateService,
        repository=operational_state_repository,
        event_publisher=event_publisher,
    )

    # Incident Use Cases
    create_incident_use_case = providers.Factory(
        CreateIncidentUseCase,
        repository=incident_repository,
        state_repository=operational_state_repository,
        event_publisher=event_publisher,
    )
    update_incident_use_case = providers.Factory(
        UpdateIncidentUseCase,
        repository=incident_repository,
        event_publisher=event_publisher,
    )
    get_incident_use_case = providers.Factory(GetIncidentUseCase, repository=incident_repository)
    list_incidents_use_case = providers.Factory(ListIncidentsUseCase, repository=incident_repository)

    # AI Intelligence Foundation
    prompt_version_manager = providers.Singleton(PromptVersionManager)
    model_gateway = providers.Singleton(ModelGateway, api_key=config.provided.gemini.api_key)
    ai_orchestrator = providers.Singleton(
        AIOrchestrator,
        gateway=model_gateway,
        version_manager=prompt_version_manager,
    )

    # Future Infrastructure/Service Providers (Placeholders for future milestones)
    gemini_client = providers.Singleton(lambda: None)
    firebase_app = providers.Singleton(lambda: None)
    maps_client = providers.Singleton(lambda: None)
