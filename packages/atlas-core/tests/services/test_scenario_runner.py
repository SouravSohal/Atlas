from datetime import UTC, datetime
from uuid import uuid4

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.services.scenario_runner import ScenarioRunner
from atlas_core.domain.services.simulation_engine import SimulationClock, SimulationContext
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


def test_scenario_runner_injection_and_tick():
    # 1. Setup Stadium & Context
    stadium = Stadium(name="Aurelia Arena", capacity=65000)
    
    n_id = uuid4()
    n_state = OperationalState(
        zone_id=n_id,
        density=CrowdDensity(value=0.30),
        queue_estimate=QueueEstimate(waiting_minutes=2),
        last_updated=datetime.now(UTC)
    )
    node = StadiumNode(
        id=n_id,
        name="Sector A Turnstiles",
        category="Entrance Gate",
        capacity=10000,
        operational_state=n_state
    )
    stadium.add_node(node)

    context = SimulationContext(
        stadium=stadium,
        clock=SimulationClock(tick_index=0)
    )

    # 2. Instantiate ScenarioRunner
    runner = ScenarioRunner(context)

    # 3. Inject scenarios
    runner.inject_scenario_events("Fire", target_node_id=n_id, trigger_tick=1)
    runner.inject_scenario_events("Lost Child", target_node_id=n_id, trigger_tick=1)

    assert len(context.scheduled_events) == 2
    assert context.scheduled_events[0].name == "Fire"
    assert context.scheduled_events[0].incident_type == IncidentType.FACILITY
    assert context.scheduled_events[1].name == "Lost Child"
    assert context.scheduled_events[1].incident_type == IncidentType.SECURITY

    # 4. Advance simulation clock & run tick
    context.clock.tick()  # tick_index transitions to 1
    assert context.clock.tick_index == 1

    runner.run_tick()

    # Verify that scheduled events triggered and created domain Incidents
    assert len(context.active_incidents) == 2
    
    fire_inc = next((i for i in context.active_incidents if i.incident_type == IncidentType.FACILITY), None)
    assert fire_inc is not None
    assert fire_inc.severity == Severity.CRITICAL
    assert "fire" in fire_inc.description

    child_inc = next((i for i in context.active_incidents if i.incident_type == IncidentType.SECURITY), None)
    assert child_inc is not None
    assert child_inc.severity == Severity.MEDIUM
    assert "child" in child_inc.description
