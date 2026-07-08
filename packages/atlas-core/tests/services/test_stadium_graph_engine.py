import pytest
from datetime import datetime, UTC
from uuid import uuid4

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.services.graph_engine import StadiumGraphEngine

def test_stadium_graph_engine_functionality():
    # 1. Setup Stadium & Nodes
    stadium = Stadium(name="Aurelia Arena", capacity=65000)
    
    n0_id = uuid4()
    n0_state = OperationalState(
        zone_id=n0_id,
        density=CrowdDensity(value=0.85),  # High density
        queue_estimate=QueueEstimate(waiting_minutes=15),
        last_updated=datetime.now(UTC)
    )
    node_0 = StadiumNode(
        id=n0_id,
        name="Gate A Ingress",
        category="Entrance Gate",
        capacity=15000,
        operational_state=n0_state,
        health_score=0.90,
        dwell_time_seconds=120.0,
        ai_importance=0.95
    )

    n1_id = uuid4()
    n1_state = OperationalState(
        zone_id=n1_id,
        density=CrowdDensity(value=0.20),
        queue_estimate=QueueEstimate(waiting_minutes=2),
        last_updated=datetime.now(UTC)
    )
    node_1 = StadiumNode(
        id=n1_id,
        name="Operations Center Hub",
        category="Operations Center",
        capacity=100,
        operational_state=n1_state,
        health_score=1.0,
        dwell_time_seconds=60.0,
        ai_importance=1.0
    )

    n2_id = uuid4()
    n2_state = OperationalState(
        zone_id=n2_id,
        density=CrowdDensity(value=0.10),
        queue_estimate=QueueEstimate(waiting_minutes=0),
        last_updated=datetime.now(UTC)
    )
    node_2 = StadiumNode(
        id=n2_id,
        name="Gate B Exit",
        category="Exit Gate",
        capacity=15000,
        operational_state=n2_state,
        health_score=1.0,
        dwell_time_seconds=60.0,
        ai_importance=0.90
    )

    stadium.add_node(node_0)
    stadium.add_node(node_1)
    stadium.add_node(node_2)

    # 2. Setup Edges
    edge_1 = StadiumEdge(
        source_id=n0_id,
        destination_id=n1_id,
        distance_meters=100.0,
        avg_walk_seconds=60.0,
        max_throughput_pax_min=1000.0,
        congestion_factor=0.40,
        emergency_access=True
    )
    edge_2 = StadiumEdge(
        source_id=n1_id,
        destination_id=n2_id,
        distance_meters=120.0,
        avg_walk_seconds=80.0,
        max_throughput_pax_min=800.0,
        congestion_factor=0.0,
        emergency_access=True
    )
    stadium.add_edge(edge_1)
    stadium.add_edge(edge_2)

    # 3. Build NetworkX Graph
    graph = StadiumGraphEngine.build_graph(stadium)
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    # Check node attributes
    n0_data = graph.nodes[str(n0_id)]
    assert n0_data["name"] == "Gate A Ingress"
    assert n0_data["density"] == 0.85

    # Check edge attributes (congestion penalized weight)
    # edge_1 penalized weight: 60 * (1 + 0.40 * 2.5) = 120.0
    assert graph[str(n0_id)][str(n1_id)]["weight"] == 120.0

    # 4. Find Shortest Route
    route = StadiumGraphEngine.find_shortest_route(graph, n0_id, n2_id)
    assert route == [str(n0_id), str(n1_id), str(n2_id)]

    # 5. Travel Time Estimation
    # total travel time: edge_1 (120s) + edge_2 (80s * (1 + 0.0)) = 200.0s
    est_time = StadiumGraphEngine.estimate_travel_time(graph, route)
    assert est_time == 200.0

    # 6. Rerouting (avoids blocked nodes)
    # Connect node_0 to node_2 directly via a longer, congested edge
    edge_direct = StadiumEdge(
        source_id=n0_id,
        destination_id=n2_id,
        distance_meters=300.0,
        avg_walk_seconds=220.0,
        max_throughput_pax_min=500.0,
        congestion_factor=0.10
    )
    stadium.add_edge(edge_direct)
    graph = StadiumGraphEngine.build_graph(stadium)

    # Shortest path should normally be: node_0 -> node_1 -> node_2 (weight: 200s)
    # If node_1 (Operations Center) is blocked, it should reroute directly node_0 -> node_2 (weight: 220s * (1 + 0.1 * 2.5) = 275s)
    rerouted_path = StadiumGraphEngine.reroute(graph, n0_id, n2_id, blocked_nodes=[n1_id])
    assert rerouted_path == [str(n0_id), str(n2_id)]

    # 7. Predict Capacity
    capacity_prediction = StadiumGraphEngine.predict_capacity(graph, n0_id)
    assert capacity_prediction["capacity_limit"] == 15000
    assert capacity_prediction["current_occupancy"] == int(15000 * 0.85)
    assert capacity_prediction["remaining_capacity"] == 15000 - int(15000 * 0.85)
    assert capacity_prediction["at_critical_limit"] is True
