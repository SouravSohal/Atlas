import os
from typing import TYPE_CHECKING

import structlog
from google.cloud import firestore

from app.config import Settings

if TYPE_CHECKING:
    from app.infrastructure.firestore.session import FirestoreSession

logger = structlog.get_logger()

class FirestoreClient:
    """Infrastructure wrapper around the Google Cloud Firestore AsyncClient."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        # Configure emulator host if provided
        if settings.firestore.emulator_host:
            os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore.emulator_host
            logger.info("Configured FIRESTORE_EMULATOR_HOST", host=settings.firestore.emulator_host)

        kwargs = {}
        if settings.gcp.project_id:
            kwargs["project"] = settings.gcp.project_id
        if settings.firestore.database:
            kwargs["database"] = settings.firestore.database

        self.client = firestore.AsyncClient(**kwargs)
        logger.info(
            "Initialized Firestore AsyncClient",
            project=settings.gcp.project_id or "default",
            database=settings.firestore.database,
            emulator=settings.firestore.emulator_host is not None,
        )

    async def close(self) -> None:
        """Closes the Firestore client connection."""
        await self.client.close()  # type: ignore[no-untyped-call]
        logger.info("Closed Firestore AsyncClient connection")

    def session(self) -> "FirestoreSession":
        """Creates a new FirestoreSession wrapper around this client."""
        from app.infrastructure.firestore.session import FirestoreSession
        return FirestoreSession(self.client)
