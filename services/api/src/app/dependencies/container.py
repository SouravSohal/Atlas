from dependency_injector import containers, providers

from app.config import get_settings


class Container(containers.DeclarativeContainer):
    """Dependency injection container for the application."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.presentation.health",
            "app.presentation.version",
            "app.main",
        ]
    )

    config = providers.Callable(get_settings)
