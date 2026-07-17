import pytest
import os
from uuid import UUID

from atlas_core.domain.services.data_loader import StadiumDataLoader
from atlas_core.domain.services.crowd_simulator import CrowdSimulationEngine, SpectatorAgent
from atlas_core.shared import resolve_seed_data_path

def test_agent_crowd_simulator_flow():
    # 1. Setup Stadium via Seed data loader
    seed_file_path = resolve_seed_data_path()
    assert seed_file_path.exists()

    with open(seed_file_path, "r", encoding="utf-8") as f:
        json_content = f.read()

    stadium = StadiumDataLoader.load_from_json(json_content)

    # 2. Instantiate Simulator
    simulator = CrowdSimulationEngine(stadium)

    # Find starting gate node (Gate 1 Ingress) and target node (Central Food Plaza)
    gate_1 = next((n for n in stadium.nodes if n.name == "Gate 1 Ingress"), None)
    food_plaza = next((n for n in stadium.nodes if n.name == "Central Food Plaza"), None)
    assert gate_1 is not None
    assert food_plaza is not None

    # 3. Spawn 20 Spectator Agents
    simulator.spawn_agents(
        count=20,
        category="regular",
        start_node_id=gate_1.id,
        end_node_id=food_plaza.id
    )

    assert len(simulator.agents) == 20
    assert simulator.agents[0].current_node_id == gate_1.id
    assert simulator.agents[0].destination_node_id == food_plaza.id
    assert len(simulator.agents[0].route) > 1

    # 4. Run movement ticks
    # Since step duration is 5 mins (300 seconds), and first edge distance is 150m (approx 110s travel time),
    # all agents should successfully cross to the next node in their route list.
    occupancies = simulator.tick(step_duration_minutes=5.0)

    # Verify that agents shifted
    first_agent = simulator.agents[0]
    assert first_agent.current_node_id != gate_1.id
    assert first_agent.route_index == 1
    
    # Gate 1 occupancy should drop to 0, and the next node on route should accumulate occupants
    assert occupancies[gate_1.id] == 0
