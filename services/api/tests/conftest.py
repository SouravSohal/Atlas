import pytest
from fastapi.testclient import TestClient

from app.dependencies import ApplicationContainer
from app.main import create_app


@pytest.fixture
def container() -> ApplicationContainer:
    """Fixture returning the DI container."""
    return ApplicationContainer()

@pytest.fixture
def client() -> TestClient:
    """Fixture returning a TestClient for the FastAPI app."""
    app = create_app()
    return TestClient(app)
