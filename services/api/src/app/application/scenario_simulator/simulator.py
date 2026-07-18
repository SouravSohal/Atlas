from uuid import UUID

from app.application.scenario_simulator.builder import ScenarioBuilder
from app.application.scenario_simulator.models import SimulationRecord
from app.application.scenario_simulator.service import SimulationService


class ScenarioSimulator:
    """Facade for the ATLAS Scenario Simulation system."""

    def __init__(self, service: SimulationService) -> None:
        self.service = service

    def create_scenario_builder(self) -> ScenarioBuilder:
        """Returns a new builder instance to configure a scenario."""
        return ScenarioBuilder()

    async def run(
        self,
        scenario_type: str,
        description: str,
        zone_id: UUID | None = None,
        severity: str = "medium",
    ) -> SimulationRecord:
        """Helper to quickly run a scenario simulation without manually using the builder."""
        builder = (
            self.create_scenario_builder()
            .with_type(scenario_type)
            .with_description(description)
            .with_severity(severity)
        )
        if zone_id:
            builder.with_zone(zone_id)
        
        scenario = builder.build()
        return await self.service.run_simulation(scenario)
