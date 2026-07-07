import firebase_admin


class FirebaseClient:
    """Wrapper client for Firebase Admin app context."""

    def __init__(self, app: firebase_admin.App) -> None:
        self.app = app
