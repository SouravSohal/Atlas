from fastapi.testclient import TestClient


def test_get_version(client: TestClient) -> None:
    # Act
    with client:
        response = client.get("/version")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "environment" in data
