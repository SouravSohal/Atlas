import json
import structlog
from typing import Dict, Set
from fastapi import WebSocket

logger = structlog.get_logger()

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts and tracks WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("WebSocket connection established", connection_count=len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Removes connection from active pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket disconnected", connection_count=len(self.active_connections))

class SubscriptionManager:
    """Manages topic-based subscriptions for connected WebSocket clients."""

    def __init__(self) -> None:
        # topic -> set of WebSockets
        self.subscriptions: Dict[str, Set[WebSocket]] = {}

    def subscribe(self, websocket: WebSocket, topic: str) -> None:
        """Subscribes WebSocket connection to a specific topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(websocket)
        logger.info("Client subscribed to topic", topic=topic)

    def unsubscribe(self, websocket: WebSocket, topic: str) -> None:
        """Unsubscribes WebSocket connection from a topic."""
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
            logger.info("Client unsubscribed from topic", topic=topic)

    def unsubscribe_all(self, websocket: WebSocket) -> None:
        """Removes WebSocket connection from all topic subscriptions."""
        for topic in list(self.subscriptions.keys()):
            self.unsubscribe(websocket, topic)

    def get_subscribers(self, topic: str) -> Set[WebSocket]:
        """Gets all WebSocket connections subscribed to a topic."""
        return self.subscriptions.get(topic, set())

class WebSocketManager:
    """Main orchestrator for managing WebSockets, subscriptions, and connection lifecycles."""

    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.subscription_manager = SubscriptionManager()

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Runs the connection receive loop and handles disconnect exceptions."""
        await self.connection_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await self.handle_message(websocket, data)
        except Exception as e:
            logger.info("WebSocket connection error or closed", error=str(e))
        finally:
            self.subscription_manager.unsubscribe_all(websocket)
            self.connection_manager.disconnect(websocket)

    async def handle_message(self, websocket: WebSocket, message_str: str) -> None:
        """Processes structured incoming subscription and ping control messages."""
        try:
            message = json.loads(message_str)
            mtype = message.get("type")
            if mtype == "subscribe":
                topic = message.get("topic")
                if topic:
                    self.subscription_manager.subscribe(websocket, topic)
                    await websocket.send_text(json.dumps({"type": "subscribed", "topic": topic}))
            elif mtype == "unsubscribe":
                topic = message.get("topic")
                if topic:
                    self.subscription_manager.unsubscribe(websocket, topic)
                    await websocket.send_text(json.dumps({"type": "unsubscribed", "topic": topic}))
            elif mtype == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
        except Exception as e:
            logger.error("Failed to handle WebSocket message", error=str(e))
