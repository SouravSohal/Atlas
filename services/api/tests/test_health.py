from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    # Act
    with client:
        response = client.get("/health")

    # Assert
    assert response.status_code == 200
    
    # Headers check
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"

    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert "app_name" in data["data"]
    assert "environment" in data["data"]

def test_readiness_check(client: TestClient) -> None:
    # Act
    with client:
        response = client.get("/ready")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["ready"] == "true"
    assert "app_name" in data["data"]
