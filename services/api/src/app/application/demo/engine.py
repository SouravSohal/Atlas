
from typing import Any
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.repositories.recommendation_repository import RecommendationRepository

from app.application.demo.factory import ScenarioFactory
from app.application.demo.registry import ScenarioRegistry
from app.application.demo.runner import ScenarioRunner
from app.application.demo.scheduler import ScenarioScheduler
from app.application.events import EventPublisher
from app.application.incidents.use_cases import CreateIncidentUseCase


class DemoScenarioEngine:
    """Facade orchestrating registered scenarios, scheduling execution, and replaying events."""

    def __init__(
        self,
        state_repository: OperationalStateRepository[OperationalState],
        recommendation_repository: RecommendationRepository[Recommendation],
        create_incident_use_case: CreateIncidentUseCase,
        event_publisher: EventPublisher,
    ) -> None:
        self.runner = ScenarioRunner(
            state_repository=state_repository,
            recommendation_repository=recommendation_repository,
            create_incident_use_case=create_incident_use_case,
            event_publisher=event_publisher,
        )
        self.scheduler = ScenarioScheduler(self.runner)
        self.registry = ScenarioRegistry()

        # Load standard scenarios using a default zone ID
        default_zone_id = "00000000-0000-0000-0000-000000000000"
        self.registry.register(ScenarioFactory.create_crowd_surge(default_zone_id))
        self.registry.register(ScenarioFactory.create_medical_emergency(default_zone_id))
        self.registry.register(ScenarioFactory.create_heavy_rain(default_zone_id))
        self.registry.register(ScenarioFactory.create_lost_child(default_zone_id))
        self.registry.register(ScenarioFactory.create_match_end(default_zone_id))

    async def play(self, name: str) -> None:
        """Finds scenario by name in registry and executes playback scheduler."""
        scenario = self.registry.get(name)
        await self.scheduler.play(scenario)

    async def pause(self) -> None:
        """Pauses currently running playback loops."""
        await self.scheduler.pause()

    async def resume(self) -> None:
        """Resumes paused playback progression."""
        await self.scheduler.resume()

    async def reset(self) -> None:
        """Resets playback state and ticks."""
        await self.scheduler.reset()

    async def set_speed(self, speed: float) -> None:
        """Configures playback speed multiplier."""
        await self.scheduler.set_speed(speed)

    def get_status(self) -> dict[str, Any]:
        """Returns details on running scenario state and step progresses."""
        curr = self.scheduler.current_scenario
        return {
            "state": self.scheduler.state.value,
            "current_scenario": curr.name if curr else None,
            "current_step": self.scheduler.current_step_idx,
            "total_steps": len(curr.steps) if curr else 0,
            "speed": self.scheduler.speed_multiplier,
        }
