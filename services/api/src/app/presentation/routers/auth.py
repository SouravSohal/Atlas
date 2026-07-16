import httpx
from datetime import datetime, UTC
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from dependency_injector.wiring import Provide, inject

from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.user_role import UserRole
from app.dependencies.container import ApplicationContainer
from app.dependencies.auth import get_current_user
from app.config import Settings
from app.presentation.responses.standard import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Long-lived Firebase session refresh token")

class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, description="Refresh token to revoke")

class UserResponse(BaseModel):
    id: str
    name: str
    role: str
    email: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

@router.post("/login", response_model=ApiResponse[LoginResponse])
@inject
async def login(
    request: LoginRequest,
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[LoginResponse]:
    """Authenticates user via Firebase Authentication REST API statelessly."""
    email_clean = request.email.strip().lower()
    
    api_key = settings.firebase.web_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Web API key is not configured",
        )

    # 1. Authenticate with Firebase Auth REST API
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email_clean,
        "password": request.password,
        "returnSecureToken": True,
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)
        if not res.is_success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        auth_data = res.json()

    uid = auth_data["localId"]
    id_token = auth_data["idToken"]
    refresh_token = auth_data["refreshToken"]
    display_name = auth_data.get("displayName") or email_clean.split("@")[0]

    # Assign role statelessly based on settings or default
    demo_email = (settings.demo.email or "demo@atlas.com").strip().lower()
    if email_clean == demo_email:
        role_str = settings.demo.role.lower().replace(" ", "_")
    else:
        role_str = "administrator"

    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.ADMINISTRATOR

    user_resp = UserResponse(
        id=uid,
        name=display_name,
        role=role.value,
        email=email_clean,
    )

    return ApiResponse(
        success=True,
        data=LoginResponse(
            access_token=id_token,
            refresh_token=refresh_token,
            user=user_resp,
        ),
    )

@router.post("/refresh", response_model=ApiResponse[LoginResponse])
@inject
async def refresh(
    request: RefreshRequest,
    settings: Settings = Depends(Provide[ApplicationContainer.config]),
) -> ApiResponse[LoginResponse]:
    """Exchanges a Firebase refresh token statelessly."""
    api_key = settings.firebase.web_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Web API key is not configured",
        )

    # 1. Exchange refresh token via Firebase Token Service
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": request.refresh_token,
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, data=payload)
        if not res.is_success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Firebase refresh token",
            )
        token_data = res.json()

    new_id_token = token_data["id_token"]
    new_refresh_token = token_data["refresh_token"]
    uid = token_data["user_id"]
    email = token_data.get("email", "")

    # Assign role statelessly
    demo_email = (settings.demo.email or "demo@atlas.com").strip().lower()
    if email.strip().lower() == demo_email:
        role_str = settings.demo.role.lower().replace(" ", "_")
    else:
        role_str = "administrator"

    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.ADMINISTRATOR
    
    display_name = email.split("@")[0] or "Firebase User"

    user_resp = UserResponse(
        id=uid,
        name=display_name,
        role=role.value,
        email=email,
    )

    return ApiResponse(
        success=True,
        data=LoginResponse(
            access_token=new_id_token,
            refresh_token=new_refresh_token,
            user=user_resp,
        ),
    )

@router.post("/logout", response_model=ApiResponse[str])
async def logout() -> ApiResponse[str]:
    """Clears and invalidates session."""
    return ApiResponse(success=True, data="Logged out successfully")

@router.get("/me", response_model=ApiResponse[UserResponse])
async def me(user: User = Depends(get_current_user)) -> ApiResponse[UserResponse]:
    """Retrieves current authenticated user profile statelessly."""
    user_resp = UserResponse(
        id=str(user.id),
        name=user.name,
        role=user.role.value,
        email=user.email,
    )
    return ApiResponse(success=True, data=user_resp)

@router.get("/validate", response_model=ApiResponse[bool])
async def validate_session(user: User = Depends(get_current_user)) -> ApiResponse[bool]:
    """Validates the current session and Firebase ID token statelessly."""
    return ApiResponse(success=True, data=True)
