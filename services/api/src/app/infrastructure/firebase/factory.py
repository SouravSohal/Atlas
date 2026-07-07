import firebase_admin
from firebase_admin import credentials

from app.config import Settings
from app.infrastructure.firebase.client import FirebaseClient
from app.infrastructure.firebase.exceptions import FirebaseException


class FirebaseClientFactory:
    """Factory to initialize and create FirebaseClient instances."""

    @staticmethod
    def create(settings: Settings) -> FirebaseClient:
        """Initializes firebase-admin and returns a FirebaseClient."""
        try:
            if not firebase_admin._apps:
                cred_path = getattr(settings, "firebase_credentials_path", None)
                if cred_path:
                    cred = credentials.Certificate(cred_path)
                    app = firebase_admin.initialize_app(cred)
                else:
                    app = firebase_admin.initialize_app()
            else:
                app = firebase_admin.get_app()
            return FirebaseClient(app)
        except Exception as e:
            raise FirebaseException(f"Failed to initialize Firebase app: {e}") from e
