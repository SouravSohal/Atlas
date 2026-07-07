import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from atlas_core.domain.events.base import DomainEvent

from app.application.events import (
    EventBus,
    EventDispatcher,
    EventPublisher,
    EventRegistry,
    InMemoryEventBus,
    register_handler,
)
from app.application.events.exceptions import (
    DuplicateHandlerRegistrationException,
    EventDispatchException,
)


class DummyEvent(DomainEvent):
    """Dummy domain event for testing."""

class DummyOtherEvent(DomainEvent):
    """Another dummy domain event for testing."""

class MockEventHandler:
    """Mock handler recording handled events."""

    def __init__(self) -> None:
        self.handled_events: list[DomainEvent] = []

    async def handle(self, event: DomainEvent) -> None:
        self.handled_events.append(event)

class SlowEventHandler:
    """Mock handler that simulates async delay."""

    def __init__(self) -> None:
        self.started = False
        self.finished = False

    async def handle(self, event: DomainEvent) -> None:
        self.started = True
        await asyncio.sleep(0.05)
        self.finished = True

class FailingEventHandler:
    """Mock handler that raises an exception."""

    async def handle(self, event: DomainEvent) -> None:
        raise RuntimeError("Intentional handler failure")

class OrderTrackingHandler:
    """Mock handler tracking processing sequence."""

    def __init__(self) -> None:
        self.received_sequence: list[str] = []

    async def handle(self, event: DomainEvent) -> None:
        # Simulate slight delay
        await asyncio.sleep(0.01)
        self.received_sequence.append(str(event.event_id))

class DummyEntity:
    """Mock aggregate root entity containing domain events."""

    def __init__(self) -> None:
        self.domain_events: list[DomainEvent] = []
        self.cleared = False

    def clear_events(self) -> None:
        self.domain_events.clear()
        self.cleared = True


def test_registry_registration_success() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()

    # Act
    registry.register(DummyEvent, handler)

    # Assert
    handlers = registry.get_handlers(DummyEvent)
    assert len(handlers) == 1
    assert handlers[0] is handler


def test_registry_duplicate_registration_fails() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register(DummyEvent, handler)

    # Act & Assert
    with pytest.raises(DuplicateHandlerRegistrationException):
        registry.register(DummyEvent, handler)


def test_registry_unregister_success() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register(DummyEvent, handler)

    # Act
    registry.unregister(DummyEvent, handler)

    # Assert
    handlers = registry.get_handlers(DummyEvent)
    assert len(handlers) == 0


def test_registry_decorator_scan() -> None:
    # Arrange
    @register_handler(DummyEvent)
    class DecoratedHandler(MockEventHandler):
        pass

    registry = EventRegistry()
    handler = DecoratedHandler()

    # Act
    registry.register_handlers([handler])

    # Assert
    handlers = registry.get_handlers(DummyEvent)
    assert len(handlers) == 1
    assert handlers[0] is handler


@pytest.mark.asyncio
async def test_dispatcher_multiple_handlers_async_dispatch() -> None:
    # Arrange
    registry = EventRegistry()
    handler1 = SlowEventHandler()
    handler2 = SlowEventHandler()
    registry.register(DummyEvent, handler1)
    registry.register(DummyEvent, handler2)
    dispatcher = EventDispatcher(registry)
    event = DummyEvent(aggregate_id=uuid4())

    # Act
    await dispatcher.dispatch(event)

    # Assert
    assert handler1.started is True
    assert handler1.finished is True
    assert handler2.started is True
    assert handler2.finished is True


@pytest.mark.asyncio
async def test_dispatcher_failure_handling_and_isolation() -> None:
    # Arrange
    registry = EventRegistry()
    success_handler = MockEventHandler()
    failing_handler = FailingEventHandler()
    registry.register(DummyEvent, success_handler)
    registry.register(DummyEvent, failing_handler)
    dispatcher = EventDispatcher(registry)
    event = DummyEvent(aggregate_id=uuid4())

    # Act & Assert
    with pytest.raises(EventDispatchException) as exc_info:
        await dispatcher.dispatch(event)

    # Assert: Success handler was still executed (isolation)
    assert len(success_handler.handled_events) == 1
    assert success_handler.handled_events[0] is event
    # Assert: Custom exception contains original handler exception
    assert len(exc_info.value.exceptions) == 1
    assert isinstance(exc_info.value.exceptions[0], RuntimeError)


@pytest.mark.asyncio
async def test_dispatcher_dispatch_many_ordering_guarantees() -> None:
    # Arrange
    registry = EventRegistry()
    handler = OrderTrackingHandler()
    registry.register(DummyEvent, handler)
    dispatcher = EventDispatcher(registry)
    
    events = [
        DummyEvent(aggregate_id=uuid4()),
        DummyEvent(aggregate_id=uuid4()),
        DummyEvent(aggregate_id=uuid4()),
    ]

    # Act
    await dispatcher.dispatch_many(events)

    # Assert
    expected_ids = [str(e.event_id) for e in events]
    assert handler.received_sequence == expected_ids


@pytest.mark.asyncio
async def test_dispatcher_dispatch_many_failure_collection() -> None:
    # Arrange
    registry = EventRegistry()
    failing_handler = FailingEventHandler()
    registry.register(DummyEvent, failing_handler)
    dispatcher = EventDispatcher(registry)

    events = [
        DummyEvent(aggregate_id=uuid4()),
        DummyEvent(aggregate_id=uuid4()),
    ]

    # Act & Assert
    with pytest.raises(EventDispatchException) as exc_info:
        await dispatcher.dispatch_many(events)

    # Assert: Collected failures from both sequential dispatches
    assert len(exc_info.value.exceptions) == 2


@pytest.mark.asyncio
async def test_in_memory_event_bus_publish_and_publish_many() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register(DummyEvent, handler)
    
    dispatcher = EventDispatcher(registry)
    bus = InMemoryEventBus(dispatcher)
    event1 = DummyEvent(aggregate_id=uuid4())
    event2 = DummyEvent(aggregate_id=uuid4())

    # Act
    await bus.publish(event1)
    await bus.publish_many([event2])

    # Assert
    assert len(handler.handled_events) == 2
    assert handler.handled_events[0] is event1
    assert handler.handled_events[1] is event2


@pytest.mark.asyncio
async def test_publisher_publish_from_entity_clears_events() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register(DummyEvent, handler)

    dispatcher = EventDispatcher(registry)
    bus = InMemoryEventBus(dispatcher)
    publisher = EventPublisher(bus)

    entity = DummyEntity()
    event = DummyEvent(aggregate_id=uuid4())
    entity.domain_events.append(event)

    # Act
    await publisher.publish_from_entity(entity)

    # Assert
    assert len(handler.handled_events) == 1
    assert handler.handled_events[0] is event
    assert entity.cleared is True
    assert len(entity.domain_events) == 0


@pytest.mark.asyncio
async def test_publisher_publish_from_entity_no_events() -> None:
    # Arrange
    bus = MagicMock(spec=EventBus)
    publisher = EventPublisher(bus)
    entity = DummyEntity()

    # Act
    await publisher.publish_from_entity(entity)

    # Assert
    bus.publish_many.assert_not_called()
    assert entity.cleared is False


@pytest.mark.asyncio
async def test_in_memory_event_bus_concurrent_publishing() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register(DummyEvent, handler)

    dispatcher = EventDispatcher(registry)
    bus = InMemoryEventBus(dispatcher)

    events = [DummyEvent(aggregate_id=uuid4()) for _ in range(5)]

    # Act: Publish concurrently
    await asyncio.gather(*(bus.publish(e) for e in events))

    # Assert: All events processed
    assert len(handler.handled_events) == 5
    # Verify all published events are in handled list
    handled_ids = {e.event_id for e in handler.handled_events}
    published_ids = {e.event_id for e in events}
    assert handled_ids == published_ids


@pytest.mark.asyncio
async def test_dispatcher_no_registered_handlers_log() -> None:
    # Arrange
    registry = EventRegistry()
    dispatcher = EventDispatcher(registry)
    event = DummyEvent(aggregate_id=uuid4())

    # Act
    await dispatcher.dispatch(event)

    # Assert
    assert len(registry.get_handlers(DummyEvent)) == 0


@pytest.mark.asyncio
async def test_publisher_publish_single_event() -> None:
    # Arrange
    bus = MagicMock(spec=EventBus)
    bus.publish = AsyncMock()
    publisher = EventPublisher(bus)
    event = DummyEvent(aggregate_id=uuid4())

    # Act
    await publisher.publish(event)

    # Assert
    bus.publish.assert_called_once_with(event)


@pytest.mark.asyncio
async def test_publisher_publish_many_empty_sequence() -> None:
    # Arrange
    bus = MagicMock(spec=EventBus)
    bus.publish_many = AsyncMock()
    publisher = EventPublisher(bus)

    # Act
    await publisher.publish_many([])

    # Assert
    bus.publish_many.assert_not_called()


@pytest.mark.asyncio
async def test_publisher_publish_from_entity_non_callable_clear() -> None:
    # Arrange
    class EntityWithNonCallableClear:
        def __init__(self) -> None:
            self.domain_events = [DummyEvent(aggregate_id=uuid4())]
            self.clear_events = "not a callable"

    bus = MagicMock(spec=EventBus)
    bus.publish_many = AsyncMock()
    publisher = EventPublisher(bus)
    entity = EntityWithNonCallableClear()

    # Act
    await publisher.publish_from_entity(entity)

    # Assert
    bus.publish_many.assert_called_once()
    assert entity.clear_events == "not a callable"


def test_registry_register_handlers_no_metadata() -> None:
    # Arrange
    registry = EventRegistry()
    class HandlerWithNoMetadata:
        async def handle(self, event: DomainEvent) -> None:
            pass

    handler = HandlerWithNoMetadata()

    # Act
    registry.register_handlers([handler])

    # Assert
    assert len(registry.get_handlers(DummyEvent)) == 0


@pytest.mark.asyncio
async def test_dispatcher_dispatch_many_standard_exception() -> None:
    # Arrange
    registry = EventRegistry()
    class GenericFailingHandler:
        async def handle(self, event: DomainEvent) -> None:
            raise KeyError("Generic key error")

    registry.register(DummyEvent, GenericFailingHandler())
    dispatcher = EventDispatcher(registry)
    events = [DummyEvent(aggregate_id=uuid4())]

    # Act & Assert
    with pytest.raises(EventDispatchException) as exc_info:
        await dispatcher.dispatch_many(events)

    # Assert
    assert len(exc_info.value.exceptions) == 1
    assert isinstance(exc_info.value.exceptions[0], KeyError)


@pytest.mark.asyncio
async def test_dispatcher_dispatch_many_generic_exception() -> None:
    # Arrange
    registry = EventRegistry()
    dispatcher = EventDispatcher(registry)
    events = [DummyEvent(aggregate_id=uuid4())]

    # Act & Assert
    with patch.object(dispatcher, "dispatch", new_callable=AsyncMock) as mock_dispatch:
        mock_dispatch.side_effect = ValueError("raw error")
        with pytest.raises(EventDispatchException) as exc_info:
            await dispatcher.dispatch_many(events)

    # Assert
    assert len(exc_info.value.exceptions) == 1
    assert isinstance(exc_info.value.exceptions[0], ValueError)
