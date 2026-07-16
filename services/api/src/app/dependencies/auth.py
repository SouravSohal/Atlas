from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dependency_injector.wiring import Provide, inject

from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.user_role import UserRole
from app.dependencies.container import ApplicationContainer
from app.infrastructure.auth.firebase import FirebaseAuthProvider

security = HTTPBearer()

@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_provider: FirebaseAuthProvider = Depends(Provide[ApplicationContainer.auth_provider]),
) -> User:
    """FastAPI dependency to retrieve the current authenticated User using Firebase Admin SDK.

    Verifies the incoming Firebase ID token, extracts user details, and returns the User.
    Does not use Firestore for user profiles.
    """
    token = credentials.credentials
    try:
        # 1. Decode and verify token using the Firebase Admin SDK provider
        decoded_token = auth_provider.verify_token(token)
        # 2. Extract user directly from decoded claims
        return auth_provider.extract_user(decoded_token)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err) or "Invalid or expired Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

def check_role(required_roles: list[UserRole]):
    """Returns a dependency that validates the current user's role."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this resource"
            )
        return user
    return _check

require_admin = check_role([UserRole.ADMINISTRATOR, UserRole.ADMIN])
require_staff = check_role([
    UserRole.ADMINISTRATOR,
    UserRole.ADMIN,
    UserRole.OPERATIONS_COMMANDER,
    UserRole.SECURITY_OFFICER,
    UserRole.MEDICAL_COORDINATOR,
    UserRole.VOLUNTEER_COORDINATOR,
    UserRole.EXECUTIVE_OBSERVER,
    UserRole.OPERATOR,
])
require_commander_or_above = check_role([
    UserRole.ADMINISTRATOR,
    UserRole.ADMIN,
    UserRole.OPERATIONS_COMMANDER,
])
