import pytest
from fastapi.testclient import TestClient

from app.dependencies.container import Container
from app.main import create_app


@pytest.fixture
def container() -> Container:
    """Fixture returning the DI container."""
    return Container()

@pytest.fixture
def client() -> TestClient:
    """Fixture returning a TestClient for the FastAPI app."""
    app = create_app()
    return TestClient(app)
