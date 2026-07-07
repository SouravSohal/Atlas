from datetime import datetime
from types import TracebackType
from typing import Any, Self
from uuid import UUID, uuid4

import pytest
from atlas_core.domain.value_objects.coordinates import Coordinates
from pydantic import BaseModel

from app.application.ports import (
    AiGateway,
    AuditGateway,
    AuthorizationService,
    Clock,
    CurrentUserProvider,
    HealthGateway,
    IdGenerator,
    MapsGateway,
    NotificationGateway,
    StorageGateway,
    Transaction,
    TransactionManager,
    TranslationGateway,
)


class DummySchema(BaseModel):
    data: str

# 1. Clock Test
def test_clock_abstract() -> None:
    with pytest.raises(TypeError):
        Clock()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_clock_mock() -> None:
    # Arrange
    now_val = datetime.now()
    class MockClock(Clock):
        async def now(self) -> datetime:
            return now_val

    clock = MockClock()
    
    # Act
    val = await clock.now()

    # Assert
    assert val == now_val


# 2. IdGenerator Test
def test_id_generator_abstract() -> None:
    with pytest.raises(TypeError):
        IdGenerator()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_id_generator_mock() -> None:
    # Arrange
    id_val = uuid4()
    class MockIdGenerator(IdGenerator):
        async def generate(self) -> UUID:
            return id_val

    generator = MockIdGenerator()

    # Act
    val = await generator.generate()

    # Assert
    assert val == id_val


# 3. Transaction Test
def test_transaction_abstract() -> None:
    with pytest.raises(TypeError):
        Transaction()  # type: ignore[abstract]

    with pytest.raises(TypeError):
        TransactionManager()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_transaction_mock() -> None:
    # Arrange
    class MockTransaction(Transaction):
        def __init__(self) -> None:
            self.committed = False
            self.rolled_back = False

        async def commit(self) -> None:
            self.committed = True

        async def rollback(self) -> None:
            self.rolled_back = True

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
        ) -> bool | None:
            await self.commit()
            return None

    class MockTransactionManager(TransactionManager):
        async def begin(self) -> Transaction:
            return MockTransaction()

    manager = MockTransactionManager()

    # Act
    tx = await manager.begin()
    assert isinstance(tx, MockTransaction)
    async with tx as active_tx:
        await active_tx.rollback()

    # Assert
    assert tx.committed is True
    assert tx.rolled_back is True


# 4. AuthorizationService Test
def test_authorization_service_abstract() -> None:
    with pytest.raises(TypeError):
        AuthorizationService()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_authorization_service_mock() -> None:
    # Arrange
    class MockAuth(AuthorizationService):
        async def authorize(self, user_id: UUID, required_role: str) -> bool:
            return required_role == "admin"

        async def authorize_resource(self, user_id: UUID, action: str, resource_id: str) -> bool:
            return action == "read"

    auth = MockAuth()
    u_id = uuid4()

    # Act & Assert
    assert await auth.authorize(u_id, "admin") is True
    assert await auth.authorize(u_id, "user") is False
    assert await auth.authorize_resource(u_id, "read", "res-1") is True


# 5. CurrentUserProvider Test
def test_current_user_provider_abstract() -> None:
    with pytest.raises(TypeError):
        CurrentUserProvider()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_current_user_provider_mock() -> None:
    # Arrange
    u_id = uuid4()
    class MockUserProvider(CurrentUserProvider):
        async def get_user_id(self) -> UUID:
            return u_id

        async def get_roles(self) -> list[str]:
            return ["admin"]

    provider = MockUserProvider()

    # Act & Assert
    assert await provider.get_user_id() == u_id
    assert await provider.get_roles() == ["admin"]


# 6. NotificationGateway Test
def test_notification_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        NotificationGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_notification_gateway_mock() -> None:
    # Arrange
    class MockNotification(NotificationGateway):
        def __init__(self) -> None:
            self.sent: list[dict[str, Any]] = []

        async def send_notification(self, recipient: str, title: str, body: str, payload: dict[str, Any] | None = None) -> None:
            self.sent.append({"recipient": recipient, "title": title, "body": body, "payload": payload})

    gateway = MockNotification()

    # Act
    await gateway.send_notification("user@test.com", "Hi", "Hello", {"info": "test"})

    # Assert
    assert len(gateway.sent) == 1
    assert gateway.sent[0]["recipient"] == "user@test.com"


# 7. TranslationGateway Test
def test_translation_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        TranslationGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_translation_gateway_mock() -> None:
    # Arrange
    class MockTranslation(TranslationGateway):
        async def translate(self, text: str, target_language: str, source_language: str | None = None) -> str:
            return f"{text}-{target_language}"

    gateway = MockTranslation()

    # Act
    res = await gateway.translate("hello", "fr")

    # Assert
    assert res == "hello-fr"


# 8. MapsGateway Test
def test_maps_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        MapsGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_maps_gateway_mock() -> None:
    # Arrange
    class MockMaps(MapsGateway):
        async def calculate_distance_meters(self, origin: Coordinates, destination: Coordinates) -> float:
            return 100.0

        async def calculate_eta_seconds(self, origin: Coordinates, destination: Coordinates) -> float:
            return 10.0

    gateway = MockMaps()
    coord1 = Coordinates(latitude=1.0, longitude=2.0)
    coord2 = Coordinates(latitude=3.0, longitude=4.0)

    # Act & Assert
    assert await gateway.calculate_distance_meters(coord1, coord2) == 100.0
    assert await gateway.calculate_eta_seconds(coord1, coord2) == 10.0


# 9. AiGateway Test
def test_ai_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        AiGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_ai_gateway_mock() -> None:
    # Arrange
    class MockAi(AiGateway):
        async def generate[T: BaseModel](self, prompt_name: str, context: Any, schema: type[T], **prompt_vars: Any) -> T:
            return schema.model_validate({"data": "mock generated"})

        async def generate_text(self, prompt_name: str, context: Any, **prompt_vars: Any) -> str:
            return "mock text"

    gateway = MockAi()

    # Act
    val = await gateway.generate("test_prompt", {}, DummySchema)
    text = await gateway.generate_text("test_prompt", {})

    # Assert
    assert val.data == "mock generated"
    assert text == "mock text"


# 10. StorageGateway Test
def test_storage_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        StorageGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_storage_gateway_mock() -> None:
    # Arrange
    class MockStorage(StorageGateway):
        def __init__(self) -> None:
            self.files: dict[str, bytes] = {}

        async def upload(self, bucket_name: str, object_name: str, data: bytes, content_type: str | None = None) -> str:
            path = f"{bucket_name}/{object_name}"
            self.files[path] = data
            return f"https://storage.mock/{path}"

        async def download(self, bucket_name: str, object_name: str) -> bytes:
            return self.files[f"{bucket_name}/{object_name}"]

        async def delete(self, bucket_name: str, object_name: str) -> None:
            del self.files[f"{bucket_name}/{object_name}"]

    gateway = MockStorage()

    # Act
    url = await gateway.upload("bucket", "file.txt", b"hello world")
    data = await gateway.download("bucket", "file.txt")
    await gateway.delete("bucket", "file.txt")

    # Assert
    assert url == "https://storage.mock/bucket/file.txt"
    assert data == b"hello world"
    assert len(gateway.files) == 0


# 11. AuditGateway Test
def test_audit_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        AuditGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_audit_gateway_mock() -> None:
    # Arrange
    class MockAudit(AuditGateway):
        def __init__(self) -> None:
            self.logs: list[dict[str, Any]] = []

        async def log_action(self, action: str, actor_id: str, resource: str, details: dict[str, Any] | None = None) -> None:
            self.logs.append({"action": action, "actor_id": actor_id, "resource": resource, "details": details})

    gateway = MockAudit()

    # Act
    await gateway.log_action("create", "user-123", "incident-456", {"reason": "test"})

    # Assert
    assert len(gateway.logs) == 1
    assert gateway.logs[0]["action"] == "create"


# 12. HealthGateway Test
def test_health_gateway_abstract() -> None:
    with pytest.raises(TypeError):
        HealthGateway()  # type: ignore[abstract]

@pytest.mark.asyncio
async def test_health_gateway_mock() -> None:
    # Arrange
    class MockHealth(HealthGateway):
        async def check_health(self) -> dict[str, bool]:
            return {"firestore": True}

    gateway = MockHealth()

    # Act
    status = await gateway.check_health()

    # Assert
    assert status == {"firestore": True}
