from fastapi.testclient import TestClient
from app.main import create_app

def test_security_headers_middleware_api_endpoints() -> None:
    # Arrange
    app = create_app()
    client = TestClient(app)
    
    # Act
    with client:
        response = client.get("/health")
        
    # Assert
    assert response.status_code == 200
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_security_headers_middleware_docs_endpoints() -> None:
    # Arrange
    app = create_app()
    client = TestClient(app)
    
    # Act
    with client:
        response = client.get("/docs")
        
    # Assert
    assert response.status_code == 200
    csp = response.headers["Content-Security-Policy"]
    assert "https://cdn.jsdelivr.net" in csp
    assert "https://fastapi.tiangolo.com" in csp
    assert "'unsafe-inline'" in csp
