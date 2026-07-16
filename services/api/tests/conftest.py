import pytest
from fastapi.testclient import TestClient

from app.dependencies import ApplicationContainer
from app.main import create_app


@pytest.fixture
def container() -> ApplicationContainer:
    """Fixture returning the DI container."""
    return ApplicationContainer()

import uuid
from app.dependencies.auth import get_current_user, require_staff, require_commander_or_above
from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.user_role import UserRole

@pytest.fixture
def client() -> TestClient:
    """Fixture returning a TestClient for the FastAPI app."""
    app = create_app()
    
    # Provide a mock admin user context to pass all security checks during unit/integration tests
    mock_user = User(
        id=uuid.uuid4(),
        name="Test Administrator",
        role=UserRole.ADMINISTRATOR,
        email="admin@test.com",
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[require_staff] = lambda: mock_user
    app.dependency_overrides[require_commander_or_above] = lambda: mock_user
    
    return TestClient(app)
