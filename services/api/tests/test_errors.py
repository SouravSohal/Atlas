from atlas_core.domain.exceptions.domain_error import DomainException
from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.main import create_app

router = APIRouter()

@router.get("/test/domain-error")
async def trigger_domain_error() -> None:
    raise DomainException("Invalid domain state")

@router.get("/test/server-error")
async def trigger_server_error() -> None:
    raise RuntimeError("Unexpected failure")

@router.get("/test/validation-error/{item_id}")
async def trigger_validation_error(item_id: int) -> dict[str, int]:
    return {"item_id": item_id}

def test_exception_handling() -> None:
    # Arrange
    app = create_app()
    app.include_router(router)
    client = TestClient(app, raise_server_exceptions=False)

    # Act: DomainException
    response = client.get("/test/domain-error")
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "Invalid domain state"
    assert data["data"] is None

    # Act: Global Exception (RuntimeError)
    response = client.get("/test/server-error")
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert "unexpected internal server error" in data["error"].lower()

    # Act: RequestValidationError
    response = client.get("/test/validation-error/not-an-int")
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "Validation failed"
    assert len(data["data"]) > 0
