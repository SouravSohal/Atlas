from datetime import UTC, datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.services.simulation_engine import (
    SimulationClock,
    SimulationContext,
    SimulationEngine,
    SimulationEvent,
    SimulationScheduler,
)
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge


@pytest.mark.asyncio
async def test_simulation_engine_cycles():
    # 1. Setup Stadium, Nodes and Edges
    stadium = Stadium(name="Aurelia Arena", capacity=65000)
    
    n0_id = uuid4()
    n0_state = OperationalState(
        zone_id=n0_id,
        density=CrowdDensity(value=0.50),  # starts at 50% density
        queue_estimate=QueueEstimate(waiting_minutes=0),
        last_updated=datetime.now(UTC)
    )
    node_0 = StadiumNode(
        id=n0_id,
        name="Gate A Ingress",
        category="Entrance Gate",
        capacity=10000,
        operational_state=n0_state
    )

    n1_id = uuid4()
    n1_state = OperationalState(
        zone_id=n1_id,
        density=CrowdDensity(value=0.0),
        queue_estimate=QueueEstimate(waiting_minutes=0),
        last_updated=datetime.now(UTC)
    )
    node_1 = StadiumNode(
        id=n1_id,
        name="Operations Center Hub",
        category="Operations Center",
        capacity=1000,
        operational_state=n1_state
    )

    stadium.add_node(node_0)
    stadium.add_node(node_1)

    edge = StadiumEdge(
        source_id=n0_id,
        destination_id=n1_id,
        distance_meters=100.0,
        avg_walk_seconds=60.0,
        max_throughput_pax_min=100.0  # 100 people/min -> 500 per 5 min step
    )
    stadium.add_edge(edge)

    # 2. Form Simulation Context & Clock
    clock = SimulationClock()
    
    # Schedule an emergency incident for Tick 1
    scheduled_event = SimulationEvent(
        name="Medical Emergency",
        target_node_id=n0_id,
        trigger_tick=1,
        incident_type=IncidentType.MEDICAL,
        severity=Severity.CRITICAL,
        description="Heat exhaustion collapse"
    )

    context = SimulationContext(
        stadium=stadium,
        clock=clock,
        scheduled_events=[scheduled_event]
    )

    # 3. Execute Tick 0 (Nominal Crowd Migration)
    tick_0 = SimulationEngine.tick(context)
    assert tick_0.tick_index == 0
    assert tick_0.time_offset == "T-120m"
    assert tick_0.incidents.active_count == 0
    # Ingress node had 5000 pax. Edges throughput max is 500 pax.
    # So 500 pax should migrate from node_0 to node_1
    assert context.node_occupancies[n0_id] == 4500
    assert context.node_occupancies[n1_id] == 500
    assert clock.tick_index == 1

    # 4. Execute Tick 1 (Triggers Incident)
    tick_1 = SimulationEngine.tick(context)
    assert tick_1.tick_index == 1
    assert tick_1.time_offset == "T-115m"
    assert len(context.active_incidents) == 1
    assert context.active_incidents[0].description == "Heat exhaustion collapse"
    assert tick_1.incidents.active_count == 1
    
    # Incident reduces health of Gate A Ingress (node_0)
    assert node_0.health_score < 1.0

    # 5. Verify Async Scheduler Loop
    scheduler = SimulationScheduler(SimulationEngine(), context)
    await scheduler.start(interval_seconds=0.01, max_ticks=2)
    assert clock.tick_index > 2
