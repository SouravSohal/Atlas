from uuid import UUID
from typing import Any, Optional
from app.application.scenario_simulator.models import Scenario

class ScenarioBuilder:
    """Builder pattern for creating Scenario configurations fluently."""

    def __init__(self) -> None:
        self._scenario_type: Optional[str] = None
        self._zone_id: Optional[UUID] = None
        self._severity: str = "medium"
        self._description: Optional[str] = None
        self._params: dict[str, Any] = {}

    def with_type(self, scenario_type: str) -> "ScenarioBuilder":
        self._scenario_type = scenario_type
        return self

    def with_zone(self, zone_id: UUID) -> "ScenarioBuilder":
        self._zone_id = zone_id
        return self

    def with_severity(self, severity: str) -> "ScenarioBuilder":
        self._severity = severity
        return self

    def with_description(self, description: str) -> "ScenarioBuilder":
        self._description = description
        return self

    def with_param(self, key: str, value: Any) -> "ScenarioBuilder":
        self._params[key] = value
        return self

    def build(self) -> Scenario:
        if not self._scenario_type:
            raise ValueError("Scenario type is required.")
        if not self._description:
            raise ValueError("Scenario description is required.")

        return Scenario(
            scenario_type=self._scenario_type,
            zone_id=self._zone_id,
            severity=self._severity,
            description=self._description,
            params=self._params,
        )
