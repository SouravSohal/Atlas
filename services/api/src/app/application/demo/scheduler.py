import asyncio

import structlog

from app.application.demo.definition import ScenarioDefinition, ScenarioState
from app.application.demo.runner import ScenarioRunner

logger = structlog.get_logger()

class ScenarioScheduler:
    """Manages playback execution timelines and controls speed scaling."""

    def __init__(self, runner: ScenarioRunner) -> None:
        self.runner = runner
        self.current_scenario: ScenarioDefinition | None = None
        self.state = ScenarioState.STOPPED
        self.current_step_idx = 0
        self.speed_multiplier = 1.0
        self._task: asyncio.Task[None] | None = None

    async def play(self, scenario: ScenarioDefinition) -> None:
        """Starts background loop playing a scenario from step 0."""
        await self.reset()
        self.current_scenario = scenario
        self.state = ScenarioState.PLAYING
        self.current_step_idx = 0
        self._task = asyncio.create_task(self._loop())
        logger.info("Demo Scenario playback started", scenario=scenario.name)

    async def pause(self) -> None:
        """Pauses timeline progression."""
        if self.state == ScenarioState.PLAYING:
            self.state = ScenarioState.PAUSED
            logger.info("Demo Scenario playback paused")

    async def resume(self) -> None:
        """Resumes paused timeline progression."""
        if self.state == ScenarioState.PAUSED:
            self.state = ScenarioState.PLAYING
            logger.info("Demo Scenario playback resumed")

    async def reset(self) -> None:
        """Stops playback loops and resets tick cursor counters."""
        self.state = ScenarioState.STOPPED
        self.current_step_idx = 0
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self.current_scenario = None
        logger.info("Demo Scenario playback reset")

    async def set_speed(self, speed: float) -> None:
        """Sets playback speed multiplier."""
        self.speed_multiplier = speed
        logger.info("Demo Scenario playback speed updated", speed=speed)

    async def _loop(self) -> None:
        try:
            while self.current_scenario and self.current_step_idx < len(self.current_scenario.steps):
                if self.state == ScenarioState.PLAYING:
                    step = self.current_scenario.steps[self.current_step_idx]
                    await self.runner.run_step(step)
                    self.current_step_idx += 1
                
                # Base tick delay (4s) scaled by speed
                delay = 4.0 / self.speed_multiplier
                await asyncio.sleep(delay)
            
            # Auto-stop on termination
            self.state = ScenarioState.STOPPED
        except asyncio.CancelledError:
            pass
