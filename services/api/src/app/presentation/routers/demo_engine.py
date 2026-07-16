import asyncio
import json
import os
import structlog
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel

from app.dependencies.container import ApplicationContainer
from app.infrastructure.streaming.broadcast import BroadcastService

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.services.data_loader import StadiumDataLoader
from atlas_core.domain.services.simulation_engine import SimulationContext, SimulationClock
from atlas_core.domain.services.scenario_runner import ScenarioRunner
from atlas_core.domain.services.recommendation_engine import StadiumRecommendationEngine

from app.dependencies.auth import require_commander_or_above
from app.infrastructure.security.rate_limiter import RateLimiterDependency

router = APIRouter(
    prefix="/demo",
    tags=["Judge Demo"],
    dependencies=[Depends(require_commander_or_above), Depends(RateLimiterDependency("simulation"))]
)
logger = structlog.get_logger()

class DemoState:
    """Maintains active in-memory state of the judge demo simulation loop."""
    def __init__(self) -> None:
        self.context: Optional[SimulationContext] = None
        self.runner: Optional[ScenarioRunner] = None
        self.active_scenario: Optional[str] = None
        self.mode: str = "autoplay"  # "autoplay" or "manual"
        self.speed: float = 1.0
        self.paused: bool = False
        self.running_task: Optional[asyncio.Task] = None

# Global demo state instance
demo_state = DemoState()

class StartDemoRequest(BaseModel):
    scenario_name: str
    mode: str = "autoplay"
    speed: float = 1.0

class SpeedDemoRequest(BaseModel):
    speed: float

async def run_autoplay_loop(broadcast_service: BroadcastService) -> None:
    """Background task executing simulation ticks and broadcasting updates via WebSockets."""
    try:
        while True:
            if demo_state.paused:
                await asyncio.sleep(0.5)
                continue

            if not demo_state.context or not demo_state.runner:
                break

            clock = demo_state.context.clock
            # Complete simulation scenarios normally have around 5 steps/ticks
            if clock.tick_index >= 5:
                logger.info("Demo scenario finished auto-run", scenario=demo_state.active_scenario)
                break

            # 1. Run simulation tick
            demo_state.runner.run_tick()

            # 2. Generate recommendations deterministically
            recs = StadiumRecommendationEngine.generate_recommendations(
                demo_state.context.stadium,
                demo_state.context.active_incidents,
                demo_state.context.incident_zones
            )

            # 3. Compile tick payload
            payload = {
                "tick_index": clock.tick_index,
                "time_offset": clock.time_offset_str,
                "scenario_name": demo_state.active_scenario,
                "stadium_health": 0.95 - (0.05 * len(demo_state.context.active_incidents)),
                "telemetry": {
                    "active_incidents_count": len(demo_state.context.active_incidents),
                    "power_draw_mw": 8.5 + (0.2 * clock.tick_index),
                },
                "incidents": [
                    {
                        "id": str(i.id),
                        "incident_type": i.incident_type.value,
                        "severity": i.severity.value,
                        "description": i.description,
                        "resolved": i.resolved
                    } for i in demo_state.context.active_incidents
                ],
                "recommendations": [
                    {
                        "action_type": r.action_type,
                        "priority": r.priority.value,
                        "confidence": r.confidence.value,
                        "details": r.details
                    } for r in recs
                ],
                "timeline": [
                    f"{clock.time_offset_str}: Active scenario {demo_state.active_scenario} step {clock.tick_index}"
                ]
            }

            # 4. Broadcast updates to WebSockets subscribers on 'telemetry' topic
            await broadcast_service.broadcast_to_topic("telemetry", payload)
            await broadcast_service.broadcast_to_topic("operational_state", payload)

            # 5. Delay based on speed factor
            sleep_duration = max(1.0, 5.0 / demo_state.speed)
            await asyncio.sleep(sleep_duration)

    except asyncio.CancelledError:
        logger.info("Demo autoplay loop cancelled")
    except Exception as e:
        logger.error("Error in demo autoplay loop", error=str(e))

@router.post("/start")
@inject
async def start_demo(
    request: StartDemoRequest,
    background_tasks: BackgroundTasks,
    broadcast_service: BroadcastService = Depends(Provide[ApplicationContainer.broadcast_service])
) -> Dict[str, Any]:
    """Initializes stadium data loader and fires the selected simulation scenario."""
    # 1. Reset state
    if demo_state.running_task:
        demo_state.running_task.cancel()
        demo_state.running_task = None

    # Load seed stadium data from local artifact path
    seed_file_path = "/home/kenx1kaneki/.gemini/antigravity-cli/brain/33650c4b-d5ca-4d21-b0b9-7dc8acb01871/stadium_seed_data.json"
    if not os.path.exists(seed_file_path):
        raise HTTPException(status_code=500, detail="Stadium database seed config file not found.")

    with open(seed_file_path, "r") as f:
        json_content = f.read()

    stadium = StadiumDataLoader.load_from_json(json_content)
    
    # 2. Build context
    clock = SimulationClock(tick_index=0)
    context = SimulationContext(stadium=stadium, clock=clock)
    runner = ScenarioRunner(context)

    # Ingress gate / target zone
    target_zone_id = stadium.nodes[0].id
    runner.inject_scenario_events(request.scenario_name, target_zone_id, trigger_tick=1)

    demo_state.context = context
    demo_state.runner = runner
    demo_state.active_scenario = request.scenario_name
    demo_state.mode = request.mode
    demo_state.speed = request.speed
    demo_state.paused = False

    # 3. Fire loop if autoplay is selected
    if request.mode == "autoplay":
        loop = asyncio.get_event_loop()
        demo_state.running_task = loop.create_task(run_autoplay_loop(broadcast_service))

    return {
        "status": "started",
        "scenario": request.scenario_name,
        "mode": request.mode,
        "speed": request.speed
    }

@router.post("/step")
@inject
async def step_demo(
    broadcast_service: BroadcastService = Depends(Provide[ApplicationContainer.broadcast_service])
) -> Dict[str, Any]:
    """Manually advances the simulation clock by 1 tick."""
    if not demo_state.context or not demo_state.runner:
        raise HTTPException(status_code=400, detail="No active demo session running. Call /start first.")

    clock = demo_state.context.clock
    demo_state.runner.run_tick()

    recs = StadiumRecommendationEngine.generate_recommendations(
        demo_state.context.stadium,
        demo_state.context.active_incidents,
        demo_state.context.incident_zones
    )

    payload = {
        "tick_index": clock.tick_index,
        "time_offset": clock.time_offset_str,
        "scenario_name": demo_state.active_scenario,
        "stadium_health": 0.95 - (0.05 * len(demo_state.context.active_incidents)),
        "telemetry": {
            "active_incidents_count": len(demo_state.context.active_incidents),
            "power_draw_mw": 8.5 + (0.2 * clock.tick_index),
        },
        "incidents": [
            {
                "id": str(i.id),
                "incident_type": i.incident_type.value,
                "severity": i.severity.value,
                "description": i.description,
                "resolved": i.resolved
            } for i in demo_state.context.active_incidents
        ],
        "recommendations": [
            {
                "action_type": r.action_type,
                "priority": r.priority.value,
                "confidence": r.confidence.value,
                "details": r.details
            } for r in recs
        ],
        "timeline": [
            f"{clock.time_offset_str}: Active scenario {demo_state.active_scenario} step {clock.tick_index}"
        ]
    }

    await broadcast_service.broadcast_to_topic("telemetry", payload)
    await broadcast_service.broadcast_to_topic("operational_state", payload)

    return {"status": "stepped", "tick_index": clock.tick_index}

@router.post("/pause")
async def pause_demo() -> Dict[str, Any]:
    """Pauses autoplay simulation updates."""
    demo_state.paused = True
    return {"status": "paused"}

@router.post("/resume")
async def resume_demo() -> Dict[str, Any]:
    """Resumes paused autoplay simulation updates."""
    demo_state.paused = False
    return {"status": "resumed"}

@router.post("/speed")
async def adjust_speed(request: SpeedDemoRequest) -> Dict[str, Any]:
    """Adjusts the execution velocity of simulation updates."""
    demo_state.speed = request.speed
    return {"status": "speed_updated", "speed": request.speed}

@router.post("/replay")
@inject
async def replay_demo(
    broadcast_service: BroadcastService = Depends(Provide[ApplicationContainer.broadcast_service])
) -> Dict[str, Any]:
    """Resets the active scenario clock back to tick index 0 and restarts loop."""
    if not demo_state.active_scenario:
        raise HTTPException(status_code=400, detail="No active scenario to replay.")

    return await start_demo(
        request=StartDemoRequest(
            scenario_name=demo_state.active_scenario,
            mode=demo_state.mode,
            speed=demo_state.speed
        ),
        background_tasks=BackgroundTasks(),
        broadcast_service=broadcast_service
    )
