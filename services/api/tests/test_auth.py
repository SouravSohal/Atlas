from unittest.mock import MagicMock, patch

import pytest
from atlas_core.domain.enums.user_role import UserRole
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.config import Settings
from app.dependencies.auth import get_current_user
from app.infrastructure.auth.firebase import FirebaseAuthProvider


@pytest.fixture
def mock_settings() -> Settings:
    return Settings()

@pytest.fixture
def auth_provider(mock_settings: Settings) -> FirebaseAuthProvider:
    with patch("firebase_admin.get_app"), patch("firebase_admin.initialize_app"):
        return FirebaseAuthProvider(mock_settings)

def test_extract_user_roles(auth_provider: FirebaseAuthProvider) -> None:
    # Arrange
    claims = {
        "uid": "user123",
        "email": "test@example.com",
        "name": "Test User",
        "role": "admin",
    }

    # Act
    user = auth_provider.extract_user(claims)

    # Assert
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == UserRole.ADMIN
    assert user.id is not None

def test_extract_user_role_fallback(auth_provider: FirebaseAuthProvider) -> None:
    # Arrange
    claims = {
        "uid": "user123",
        "email": "test@example.com",
        "name": "",
        "role": "invalid_role",
    }

    # Act
    user = auth_provider.extract_user(claims)

    # Assert
    assert user.role == UserRole.FAN
    assert user.name == "test"

@patch("firebase_admin.auth.verify_id_token")
def test_verify_token_success(mock_verify: MagicMock, auth_provider: FirebaseAuthProvider) -> None:
    # Arrange
    mock_verify.return_value = {"uid": "user123"}

    # Act
    result = auth_provider.verify_token("valid_token")

    # Assert
    assert result == {"uid": "user123"}
    mock_verify.assert_called_once_with("valid_token", check_revoked=False)

@patch("firebase_admin.auth.verify_id_token")
def test_verify_token_failure(mock_verify: MagicMock, auth_provider: FirebaseAuthProvider) -> None:
    # Arrange
    mock_verify.side_effect = Exception("Invalid token")

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid or expired authentication token"):
        auth_provider.verify_token("invalid_token")

@pytest.mark.asyncio
async def test_get_current_user_dependency_success(auth_provider: FirebaseAuthProvider) -> None:
    # Arrange
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
    decoded = {"uid": "user123", "email": "test@example.com", "role": "operator"}

    auth_provider.verify_token = MagicMock(return_value=decoded)  # type: ignore

    # Act
    user = await get_current_user(credentials=credentials, auth_provider=auth_provider)

    # Assert
    assert user.email == "test@example.com"
    assert user.role == UserRole.OPERATOR

@pytest.mark.asyncio
async def test_get_current_user_dependency_unauthorized(auth_provider: FirebaseAuthProvider) -> None:
    # Arrange
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
    auth_provider.verify_token = MagicMock(side_effect=ValueError("Token invalid"))  # type: ignore

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, auth_provider=auth_provider)

    assert exc_info.value.status_code == 401
    assert "Token invalid" in exc_info.value.detail
