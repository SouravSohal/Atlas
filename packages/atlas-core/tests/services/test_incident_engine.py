import pytest
from datetime import datetime, UTC
from uuid import uuid4

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.services.incident_engine import IncidentEngine

def test_incident_engine_lifecycle_and_propagation():
    # 1. Setup Stadium, Nodes and Edges
    stadium = Stadium(name="Aurelia Arena", capacity=65000)
    
    n0_id = uuid4()
    n0_state = OperationalState(
        zone_id=n0_id,
        density=CrowdDensity(value=0.20),
        queue_estimate=QueueEstimate(waiting_minutes=2),
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
        max_throughput_pax_min=100.0,
        congestion_factor=0.0
    )
    stadium.add_edge(edge)

    # 2. Instantiate Engine
    engine = IncidentEngine()

    # 3. Detection Phase
    incident = engine.detect_incident(
        stadium=stadium,
        incident_type=IncidentType.MEDICAL,
        severity=Severity.HIGH,
        description="Cardiac distress Sector 104",
        target_node_id=n0_id
    )

    assert incident is not None
    assert engine.incident_phases[incident.id] == "detected"
    assert incident.resolved is False

    # 4. Propagation Phase
    active_incidents = [incident]
    incident_zones = {incident.id: n0_id}
    
    engine.propagate_risks(stadium, active_incidents, incident_zones)

    # Health score drops from 1.0 -> 0.75
    assert node_0.health_score == 0.75
    # Wait queue rises from 2 -> 12 minutes
    assert node_0.operational_state.queue_estimate.waiting_minutes == 12
    # Edge congestion spikes from 0.0 -> 0.35, max throughput chokes from 100.0 -> 50.0
    assert edge.congestion_factor == 0.35
    assert edge.max_throughput_pax_min == 50.0
    assert engine.incident_phases[incident.id] == "propagated"

    # 5. Mitigation Phase
    engine.apply_mitigation(incident, strategy="Dispatch responder squad Alpha")
    assert engine.incident_phases[incident.id] == "mitigated"
    assert engine.mitigation_strategies[incident.id] == "Dispatch responder squad Alpha"

    # 6. Resolution Phase
    engine.resolve_incident(incident)
    assert incident.resolved is True
    assert engine.incident_phases[incident.id] == "resolved"

    # 7. Recovery Phase
    engine.execute_recovery(stadium, incident, n0_id)
    assert engine.incident_phases[incident.id] == "recovered"
    # Node health recovers from 0.75 -> 1.0
    assert node_0.health_score == 1.0
    # Wait queue drops back from 12 -> 2 minutes
    assert node_0.operational_state.queue_estimate.waiting_minutes == 2
    # Edge congestion drops from 0.35 -> 0.0, max throughput capacity is restored
    assert edge.congestion_factor == 0.0
    assert edge.max_throughput_pax_min == 100.0
