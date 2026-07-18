
from app.application.scenario_simulator.models import Scenario

SUPPORTED_SCENARIOS: set[str] = {
    "Gate Closure",
    "Crowd Surge",
    "Medical Emergency",
    "Heavy Rain",
    "Public Transport Delay",
    "Power Failure",
    "VIP Arrival",
    "Security Incident",
    "Lost Child",
    "Evacuation",
}

VALID_SEVERITIES: set[str] = {"low", "medium", "high", "critical"}

class ScenarioValidator:
    """Validates simulation scenarios before execution."""

    def validate(self, scenario: Scenario) -> None:
        """Raises ValueError if the scenario configuration is invalid."""
        if scenario.scenario_type not in SUPPORTED_SCENARIOS:
            raise ValueError(
                f"Unsupported scenario type: '{scenario.scenario_type}'. "
                f"Supported types are: {', '.join(SUPPORTED_SCENARIOS)}"
            )

        if scenario.severity.lower() not in VALID_SEVERITIES:
            raise ValueError(
                f"Invalid severity level: '{scenario.severity}'. "
                f"Supported levels are: {', '.join(VALID_SEVERITIES)}"
            )

        if not scenario.description.strip():
            raise ValueError("Scenario description cannot be empty.")
