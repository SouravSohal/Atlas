import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_judge_demo_engine_endpoints() -> None:
    client = TestClient(app)

    # 1. Start Demo
    response = client.post("/demo/start", json={
        "scenario_name": "Fire",
        "mode": "manual",
        "speed": 1.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert data["scenario"] == "Fire"
    assert data["mode"] == "manual"

    # 2. Advance Step
    response = client.post("/demo/step")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stepped"
    assert data["tick_index"] == 1

    # 3. Pause Demo
    response = client.post("/demo/pause")
    assert response.status_code == 200
    assert response.json()["status"] == "paused"

    # 4. Resume Demo
    response = client.post("/demo/resume")
    assert response.status_code == 200
    assert response.json()["status"] == "resumed"

    # 5. Adjust Speed
    response = client.post("/demo/speed", json={"speed": 2.5})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "speed_updated"
    assert data["speed"] == 2.5

    # 6. Replay Demo
    response = client.post("/demo/replay")
    assert response.status_code == 200
    assert response.json()["status"] == "started"
