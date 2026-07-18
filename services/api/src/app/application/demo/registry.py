
from app.application.demo.definition import ScenarioDefinition


class ScenarioRegistry:
    """Registry maintaining active demo scenario definitions."""

    def __init__(self) -> None:
        self._scenarios: dict[str, ScenarioDefinition] = {}

    def register(self, definition: ScenarioDefinition) -> None:
        """Adds a scenario definition to the registry."""
        self._scenarios[definition.name] = definition

    def get(self, name: str) -> ScenarioDefinition:
        """Retrieves a scenario definition by name."""
        if name not in self._scenarios:
            raise KeyError(f"Scenario '{name}' is not registered.")
        return self._scenarios[name]

    def list_all(self) -> list[str]:
        """Lists all registered scenario names."""
        return list(self._scenarios.keys())
