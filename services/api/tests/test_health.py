from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    # Act
    with client:
        response = client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "environment" in data
