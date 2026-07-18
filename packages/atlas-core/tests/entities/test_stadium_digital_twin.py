from datetime import UTC, datetime
from uuid import uuid4

import pytest

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.crowd_state import CrowdState
from atlas_core.domain.value_objects.incident_state import IncidentState
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.value_objects.simulation_tick import SimulationTick
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge
from atlas_core.domain.value_objects.telemetry_snapshot import TelemetrySnapshot


def test_stadium_digital_twin_lifecycle():
    # 1. Create a stadium aggregate
    stadium = Stadium(
        name="Aurelia Arena",
        capacity=65000
    )
    assert stadium.name == "Aurelia Arena"
    assert stadium.capacity == 65000
    assert len(stadium.nodes) == 0
    assert len(stadium.edges) == 0
    assert len(stadium.history_ticks) == 0

    # 2. Add StadiumNode
    zone_id = uuid4()
    op_state = OperationalState(
        zone_id=zone_id,
        density=CrowdDensity(value=0.45),
        queue_estimate=QueueEstimate(waiting_minutes=5),
        last_updated=datetime.now(UTC)
    )
    
    node_1 = StadiumNode(
        name="Gate A Ingress",
        category="Entrance Gate",
        capacity=15000,
        operational_state=op_state,
        health_score=0.98,
        dwell_time_seconds=120.0,
        ai_importance=0.95
    )
    stadium.add_node(node_1)
    assert len(stadium.nodes) == 1
    assert stadium.nodes[0].name == "Gate A Ingress"
    assert stadium.nodes[0].operational_state.density.value == 0.45

    # 3. Add second node and link with edge
    zone_id_2 = uuid4()
    op_state_2 = OperationalState(
        zone_id=zone_id_2,
        density=CrowdDensity(value=0.15),
        queue_estimate=QueueEstimate(waiting_minutes=0),
        last_updated=datetime.now(UTC)
    )
    node_2 = StadiumNode(
        name="Volunteer Base Alpha",
        category="Volunteer Station",
        capacity=100,
        operational_state=op_state_2,
        health_score=1.0,
        dwell_time_seconds=60.0,
        ai_importance=0.90
    )
    stadium.add_node(node_2)

    edge = StadiumEdge(
        source_id=node_1.id,
        destination_id=node_2.id,
        distance_meters=150.0,
        avg_walk_seconds=110.0,
        max_throughput_pax_min=1500.0,
        congestion_factor=0.15,
        emergency_access=True
    )
    stadium.add_edge(edge)
    assert len(stadium.edges) == 1
    assert stadium.edges[0].distance_meters == 150.0

    # 4. Check duplicate node error
    with pytest.raises(ValueError):
        stadium.add_node(node_1)

    # 5. Check edge node existence validation
    invalid_edge = StadiumEdge(
        source_id=node_1.id,
        destination_id=uuid4(),
        distance_meters=100.0,
        avg_walk_seconds=60.0,
        max_throughput_pax_min=1000.0
    )
    with pytest.raises(ValueError):
        stadium.add_edge(invalid_edge)

    # 6. Record SimulationTick
    now = datetime.now(UTC)
    telemetry = TelemetrySnapshot(
        timestamp=now,
        power_draw_mw=6.5,
        sensor_status=0.98,
        cctv_online_rate=0.99
    )
    crowd = CrowdState(
        occupancy_percentage=0.65,
        avg_wait_minutes=8.5,
        peak_density_pax_m2=2.4
    )
    incidents = IncidentState(
        active_count=1,
        critical_count=0,
        warning_count=1
    )
    tick = SimulationTick(
        tick_index=1,
        time_offset="T-30m",
        telemetry=telemetry,
        crowd=crowd,
        incidents=incidents
    )
    stadium.record_tick(tick)
    assert len(stadium.history_ticks) == 1
    assert stadium.history_ticks[0].time_offset == "T-30m"
    assert stadium.history_ticks[0].telemetry.power_draw_mw == 6.5
