from unittest.mock import MagicMock, patch

import pytest

from app.config import Settings
from app.infrastructure.ai import AiClient, AiClientFactory, AiException
from app.infrastructure.config import ConfigClient, ConfigClientFactory
from app.infrastructure.firebase import FirebaseClient, FirebaseClientFactory, FirebaseException
from app.infrastructure.firestore import FirestoreClient, FirestoreClientFactory
from app.infrastructure.logging import LoggingClient, LoggingClientFactory
from app.infrastructure.maps import MapsClient, MapsClientFactory
from app.infrastructure.monitoring import (
    MonitoringClient,
    MonitoringClientFactory,
)
from app.infrastructure.storage import StorageClient, StorageClientFactory, StorageException


# 1. Config tests
def test_config_client_and_factory() -> None:
    # Arrange
    mock_settings = MagicMock(spec=Settings)
    mock_settings.app_name = "ATLAS"

    with patch("app.infrastructure.config.factory.get_settings", return_value=mock_settings):
        # Act
        client = ConfigClientFactory.create()
        val = client.get("app_name")
        default_val = client.get("non_existent", "default")

        # Assert
        assert isinstance(client, ConfigClient)
        assert val == "ATLAS"
        assert default_val == "default"


# 2. Logging tests
def test_logging_client_and_factory() -> None:
    # Act
    client = LoggingClientFactory.create()
    logger = client.get_logger()

    # Assert
    assert isinstance(client, LoggingClient)
    assert logger is not None


# 3. Monitoring tests
@pytest.mark.asyncio
async def test_monitoring_client_and_factory() -> None:
    # Act
    client = MonitoringClientFactory.create()

    # Assert
    assert isinstance(client, MonitoringClient)
    # Should not raise exception
    await client.record_metric("cpu_usage", 85.5, {"env": "prod"})


# 4. Firebase tests
def test_firebase_client_and_factory_default() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.firebase_credentials_path = None

    with patch("firebase_admin.initialize_app") as mock_init, \
         patch("firebase_admin.get_app"), \
         patch("firebase_admin._apps", []):
        
        mock_init.return_value = MagicMock()

        # Act
        client = FirebaseClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, FirebaseClient)
        mock_init.assert_called_once()

def test_firebase_client_and_factory_with_credentials() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.firebase_credentials_path = "/path/to/credentials.json"

    with patch("firebase_admin.initialize_app") as mock_init, \
         patch("firebase_admin.credentials.Certificate") as mock_cert, \
         patch("firebase_admin._apps", []):
        
        mock_init.return_value = MagicMock()
        mock_cert.return_value = MagicMock()

        # Act
        client = FirebaseClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, FirebaseClient)
        mock_cert.assert_called_once_with("/path/to/credentials.json")
        mock_init.assert_called_once()

def test_firebase_client_and_factory_existing_app() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_app = MagicMock()

    with patch("firebase_admin.initialize_app") as mock_init, \
         patch("firebase_admin.get_app", return_value=mock_app) as mock_get, \
         patch("firebase_admin._apps", [mock_app]):

        # Act
        client = FirebaseClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, FirebaseClient)
        mock_init.assert_not_called()
        mock_get.assert_called_once()

def test_firebase_client_and_factory_exception() -> None:
    # Arrange
    mock_settings = MagicMock()

    with patch("firebase_admin.initialize_app", side_effect=RuntimeError("Firebase init error")), \
         patch("firebase_admin._apps", []), \
         pytest.raises(FirebaseException, match="Failed to initialize Firebase app"):
        FirebaseClientFactory.create(mock_settings)


# 5. Firestore tests
def test_firestore_client_factory() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.firestore.emulator_host = None
    mock_settings.gcp.project_id = "test-project"
    mock_settings.firestore.database = "test-db"

    with patch("google.cloud.firestore.AsyncClient") as mock_async_client:
        # Act
        client = FirestoreClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, FirestoreClient)
        mock_async_client.assert_called_once()


# 6. AI tests
def test_ai_client_and_factory() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.gemini.api_key = "test-gemini-key"

    with patch("google.genai.Client") as mock_genai_client:
        # Act
        client = AiClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, AiClient)
        mock_genai_client.assert_called_once_with(api_key="test-gemini-key")

def test_ai_client_factory_missing_key() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.gemini.api_key = None

    # Act & Assert
    with pytest.raises(AiException, match="Gemini API key is not configured"):
        AiClientFactory.create(mock_settings)


# 7. Maps tests
def test_maps_client_and_factory() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.maps_api_key = "test-maps-key"

    # Act
    client = MapsClientFactory.create(mock_settings)

    # Assert
    assert isinstance(client, MapsClient)
    assert client.api_key == "test-maps-key"


# 8. Storage tests
def test_storage_client_and_factory() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.gcp.project_id = "test-project"

    with patch("google.cloud.storage.Client") as mock_storage_client:
        # Act
        client = StorageClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, StorageClient)
        mock_storage_client.assert_called_once_with(project="test-project")

def test_storage_client_factory_exception() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.gcp.project_id = "test-project"

    with patch("google.cloud.storage.Client", side_effect=Exception("Storage init error")), \
         pytest.raises(StorageException, match="Failed to initialize StorageClient"):
        StorageClientFactory.create(mock_settings)
