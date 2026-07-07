from uuid import uuid4

import pytest
from atlas_core.domain.events.base import DomainEvent

from app.application.events import (
    EventDispatcher,
    EventHandler,
    EventPublisher,
    EventRegistry,
    InMemoryEventBus,
    register_handler,
)


class MockEvent(DomainEvent):
    """Test domain event."""

class MockEventOther(DomainEvent):
    """Another test domain event."""

@register_handler(MockEvent)
class MockEventHandler(EventHandler[MockEvent]):
    """Test event handler."""

    def __init__(self) -> None:
        self.handled_events: list[MockEvent] = []

    async def handle(self, event: MockEvent) -> None:
        self.handled_events.append(event)

class FailingEventHandler(EventHandler[MockEvent]):
    """Test handler that fails."""

    async def handle(self, event: MockEvent) -> None:
        raise RuntimeError("Handler failed intentionally")

def test_event_registry_manual() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()

    # Act
    registry.register(MockEvent, handler)

    # Assert
    handlers = registry.get_handlers(MockEvent)
    assert len(handlers) == 1
    assert handlers[0] is handler

def test_event_registry_decorator_scan() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()

    # Act
    registry.register_handlers([handler])

    # Assert
    handlers = registry.get_handlers(MockEvent)
    assert len(handlers) == 1
    assert handlers[0] is handler

@pytest.mark.asyncio
async def test_event_dispatcher_success() -> None:
    # Arrange
    registry = EventRegistry()
    handler1 = MockEventHandler()
    handler2 = MockEventHandler()
    registry.register_handlers([handler1, handler2])

    dispatcher = EventDispatcher(registry)
    event = MockEvent(aggregate_id=uuid4())

    # Act
    await dispatcher.dispatch(event)

    # Assert
    assert len(handler1.handled_events) == 1
    assert handler1.handled_events[0] is event
    assert len(handler2.handled_events) == 1
    assert handler2.handled_events[0] is event

@pytest.mark.asyncio
async def test_event_dispatcher_no_handlers() -> None:
    # Arrange
    registry = EventRegistry()
    dispatcher = EventDispatcher(registry)
    event = MockEvent(aggregate_id=uuid4())

    # Act & Assert (Should not raise exception)
    await dispatcher.dispatch(event)

@pytest.mark.asyncio
async def test_event_dispatcher_failing_handler_isolation() -> None:
    # Arrange
    registry = EventRegistry()
    success_handler = MockEventHandler()
    failing_handler = FailingEventHandler()
    
    # Manually register the failing handler
    registry.register(MockEvent, failing_handler)
    registry.register_handlers([success_handler])

    dispatcher = EventDispatcher(registry)
    event = MockEvent(aggregate_id=uuid4())

    # Act & Assert (Failing handler error is caught, success handler runs)
    await dispatcher.dispatch(event)

    assert len(success_handler.handled_events) == 1
    assert success_handler.handled_events[0] is event

@pytest.mark.asyncio
async def test_in_memory_event_bus() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register_handlers([handler])

    dispatcher = EventDispatcher(registry)
    bus = InMemoryEventBus(dispatcher)
    event = MockEvent(aggregate_id=uuid4())

    # Act
    await bus.publish(event)

    # Assert
    assert len(handler.handled_events) == 1

@pytest.mark.asyncio
async def test_event_publisher() -> None:
    # Arrange
    registry = EventRegistry()
    handler = MockEventHandler()
    registry.register_handlers([handler])

    dispatcher = EventDispatcher(registry)
    bus = InMemoryEventBus(dispatcher)
    publisher = EventPublisher(bus)
    event1 = MockEvent(aggregate_id=uuid4())
    event2 = MockEvent(aggregate_id=uuid4())

    # Act: publish single
    await publisher.publish(event1)
    # Act: publish empty list (no-op)
    await publisher.publish_many([])
    # Act: publish many
    await publisher.publish_many([event2])

    # Assert
    assert len(handler.handled_events) == 2
    assert handler.handled_events[0] is event1
    assert handler.handled_events[1] is event2
