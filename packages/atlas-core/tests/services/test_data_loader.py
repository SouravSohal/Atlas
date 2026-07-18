from atlas_core.domain.services.data_loader import StadiumDataLoader
from atlas_core.shared import resolve_seed_data_path


def test_stadium_data_loader_parsing():
    # 1. Load the generated seed JSON dataset
    seed_file_path = resolve_seed_data_path()
    
    assert seed_file_path.exists(), "Stadium seed data JSON file must exist."

    with open(seed_file_path, encoding="utf-8") as f:
        json_content = f.read()

    # 2. Run loader
    stadium = StadiumDataLoader.load_from_json(json_content)

    # 3. Assert correct aggregate roots conversions
    assert stadium.name == "Aurelia Arena"
    assert stadium.capacity == 65000
    assert len(stadium.nodes) == 10
    assert len(stadium.edges) == 10

    # 4. Verify specific node translations (Gate 1 Ingress)
    gate_1 = next((n for n in stadium.nodes if n.name == "Gate 1 Ingress"), None)
    assert gate_1 is not None
    assert gate_1.category == "Entrance Gate"
    assert gate_1.capacity == 15000
    
    # 45 density should map to 0.45 float value in CrowdDensity
    assert gate_1.operational_state.density.value == 0.45
    assert gate_1.operational_state.queue_estimate.waiting_minutes == 5
    assert gate_1.health_score == 0.98

    # 5. Verify edges source and target mapping consistency
    edge_g1_vol = next((e for e in stadium.edges if e.source_id == gate_1.id), None)
    assert edge_g1_vol is not None
    assert edge_g1_vol.distance_meters == 150.0
    assert edge_g1_vol.avg_walk_seconds == 110.0
    assert edge_g1_vol.max_throughput_pax_min == 1500.0
    assert edge_g1_vol.congestion_factor == 0.15
    assert edge_g1_vol.emergency_access is True
