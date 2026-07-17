import uuid
from typing import Any

import firebase_admin
import structlog
from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.user_role import UserRole
from firebase_admin import auth, credentials

from app.config import Settings

logger = structlog.get_logger()

class FirebaseAuthProvider:
    """Infrastructure provider for verifying Firebase ID tokens using the Firebase Admin SDK."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        try:
            firebase_admin.get_app()
        except ValueError:
            if settings.gcp.credentials_path:
                cred = credentials.Certificate(settings.gcp.credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()

    def verify_token(self, id_token: str) -> dict[str, Any]:
        """Verifies the Firebase ID token and returns the decoded claims.

        Raises:
            ValueError: If the token is invalid or expired.
        """
        try:
            decoded: dict[str, Any] = auth.verify_id_token(id_token, check_revoked=False)
            return decoded
        except Exception as e:
            logger.warning("Firebase token verification failed", error=str(e))
            raise ValueError("Invalid or expired authentication token") from e

    def extract_user(self, decoded_token: dict[str, Any]) -> User:
        """Extracts claims and reconstructs a User domain entity from the decoded token.

        Uses UUID5 to deterministically map the Firebase string UID to a UUID.
        """
        uid = decoded_token.get("uid", "")
        email = decoded_token.get("email", "")
        name = decoded_token.get("name", "") or decoded_token.get("email", "").split("@")[0] or "Firebase User"

        # Deterministic UUID mapping
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, f"firebase:{uid}")

        # Extract role: override for demo account, otherwise default to fan
        demo_email = self.settings.demo.email.strip().lower() if self.settings.demo.email else ""
        if email.strip().lower() == demo_email:
            role_str = self.settings.demo.role.lower().replace(" ", "_")
        else:
            role_str = decoded_token.get("role", "fan").lower().replace(" ", "_")

        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.FAN

        return User(
            id=user_uuid,
            name=name,
            role=role,
            email=email,
        )
