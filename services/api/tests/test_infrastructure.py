from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from app.config import Settings
from app.infrastructure.common import (
    CommonInfrastructureClient,
    CommonInfrastructureClientFactory,
    CommonInfrastructureHealthCheck,
)
from app.infrastructure.config import (
    ConfigClient,
    ConfigClientFactory,
    ConfigHealthCheck,
)
from app.infrastructure.firebase import (
    FirebaseClient,
    FirebaseClientFactory,
    FirebaseException,
    FirebaseHealthCheck,
)
from app.infrastructure.firestore import (
    FirestoreClient,
    FirestoreClientFactory,
    FirestoreHealthCheck,
)
from app.infrastructure.logging import (
    LoggingClient,
    LoggingClientFactory,
    LoggingHealthCheck,
)
from app.infrastructure.maps import MapsClient, MapsClientFactory, MapsHealthCheck
from app.infrastructure.monitoring import (
    MonitoringClient,
    MonitoringClientFactory,
    MonitoringHealthCheck,
)
from app.infrastructure.storage import (
    StorageClient,
    StorageClientFactory,
    StorageException,
    StorageHealthCheck,
)
from app.infrastructure.vertex_ai import (
    VertexAiClient,
    VertexAiClientFactory,
    VertexAiException,
    VertexAiHealthCheck,
)


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


@pytest.mark.asyncio
async def test_config_health_check() -> None:
    # Arrange
    mock_settings = MagicMock()
    client = ConfigClient(mock_settings)
    check = ConfigHealthCheck(client)

    # Act & Assert
    assert await check.check_health() is True

    client.settings = None  # type: ignore[assignment]
    assert await check.check_health() is False


# 2. Logging tests
def test_logging_client_and_factory() -> None:
    # Act
    client = LoggingClientFactory.create()
    logger = client.get_logger()

    # Assert
    assert isinstance(client, LoggingClient)
    assert logger is not None


@pytest.mark.asyncio
async def test_logging_health_check() -> None:
    # Arrange
    client = LoggingClientFactory.create()
    check = LoggingHealthCheck(client)

    # Act & Assert
    assert await check.check_health() is True


# 3. Monitoring tests
@pytest.mark.asyncio
async def test_monitoring_client_and_factory() -> None:
    # Act
    client = MonitoringClientFactory.create()
    check = MonitoringHealthCheck(client)

    # Assert
    assert isinstance(client, MonitoringClient)
    # Should not raise exception
    await client.record_metric("cpu_usage", 85.5, {"env": "prod"})
    assert await check.check_health() is True


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


@pytest.mark.asyncio
async def test_firebase_health_check() -> None:
    # Arrange
    mock_app = MagicMock()
    client = FirebaseClient(mock_app)
    check = FirebaseHealthCheck(client)

    # Act & Assert
    assert await check.check_health() is True

    client.app = None
    assert await check.check_health() is False

    # Exception path
    mock_failing_client = MagicMock()
    type(mock_failing_client).app = PropertyMock(side_effect=RuntimeError("Firebase app error"))
    check_fail = FirebaseHealthCheck(mock_failing_client)
    assert await check_fail.check_health() is False


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


@pytest.mark.asyncio
async def test_firestore_health_check() -> None:
    # Arrange
    mock_client = MagicMock()
    from collections.abc import AsyncGenerator
    
    async def mock_collections() -> AsyncGenerator[None, None]:
        if False:
            yield

    mock_client.client.collections.return_value = mock_collections()
    check = FirestoreHealthCheck(mock_client)

    # Act & Assert
    assert await check.check_health() is True

    # Error path
    mock_client.client.collections.side_effect = Exception("Db failure")
    assert await check.check_health() is False


# 6. Vertex AI tests
def test_vertex_ai_client_and_factory() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.gemini.api_key = "test-gemini-key"

    with patch("google.genai.Client") as mock_genai_client:
        # Act
        client = VertexAiClientFactory.create(mock_settings)

        # Assert
        assert isinstance(client, VertexAiClient)
        mock_genai_client.assert_called_once_with(api_key="test-gemini-key")

def test_vertex_ai_client_factory_missing_key() -> None:
    # Arrange
    mock_settings = MagicMock()
    mock_settings.gemini.api_key = None

    # Act & Assert
    with pytest.raises(VertexAiException, match="Gemini/Vertex AI API key is not configured"):
        VertexAiClientFactory.create(mock_settings)


@pytest.mark.asyncio
async def test_vertex_ai_health_check() -> None:
    # Arrange
    mock_client = MagicMock()
    check = VertexAiHealthCheck(mock_client)

    # Act & Assert
    assert await check.check_health() is True

    mock_client.client = None
    assert await check.check_health() is False

    # Exception path
    mock_failing_client = MagicMock()
    type(mock_failing_client).client = PropertyMock(side_effect=RuntimeError("AI client error"))
    check_fail = VertexAiHealthCheck(mock_failing_client)
    assert await check_fail.check_health() is False
    assert await check.check_health() is False


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


@pytest.mark.asyncio
async def test_maps_health_check() -> None:
    # Arrange
    client = MapsClient("key")
    check = MapsHealthCheck(client)

    # Act & Assert
    assert await check.check_health() is True


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


@pytest.mark.asyncio
async def test_storage_health_check() -> None:
    # Arrange
    mock_client = MagicMock()
    check = StorageHealthCheck(mock_client)

    # Act & Assert
    assert await check.check_health() is True

    mock_client.client = None
    assert await check.check_health() is False

    # Exception path
    mock_failing_client = MagicMock()
    type(mock_failing_client).client = PropertyMock(side_effect=RuntimeError("Storage client error"))
    check_fail = StorageHealthCheck(mock_failing_client)
    assert await check_fail.check_health() is False


# 9. Common infrastructure tests
def test_common_infrastructure_client_and_factory() -> None:
    # Act
    client = CommonInfrastructureClientFactory.create()

    # Assert
    assert isinstance(client, CommonInfrastructureClient)


@pytest.mark.asyncio
async def test_common_health_check() -> None:
    # Arrange
    client = CommonInfrastructureClientFactory.create()
    check = CommonInfrastructureHealthCheck(client)

    # Act & Assert
    assert await check.check_health() is True
