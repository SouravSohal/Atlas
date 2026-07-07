from atlas_core.domain.entities.user import User
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies.container import ApplicationContainer
from app.infrastructure.auth.firebase import FirebaseAuthProvider

security = HTTPBearer()

@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_provider: FirebaseAuthProvider = Depends(Provide[ApplicationContainer.auth_provider]),
) -> User:
    """FastAPI dependency to retrieve the current authenticated User.

    Extracts the Bearer token, verifies it via Firebase, and returns the User entity.
    """
    token = credentials.credentials
    try:
        decoded_token = auth_provider.verify_token(token)
        return auth_provider.extract_user(decoded_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
